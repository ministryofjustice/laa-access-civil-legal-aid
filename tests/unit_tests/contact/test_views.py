from unittest.mock import patch, MagicMock, PropertyMock
from flask import url_for
from flask_wtf import FlaskForm
from app.contact.forms import ReasonsForContactingForm
from app.contact.views import (
    ContactUs,
    FastTrackedContactUs,
    FinancialAssessmentReason,
    FinancialAssessmentStatus,
)
from app.contact.urls import EligibleContactUsPage
from app.means_test.views import MeansTest
from app.categories.constants import DOMESTIC_ABUSE
from app.categories.models import CategoryAnswer
from app.session import Session
from app.means_test.api import EligibilityState


class TestContactUsView:
    def test_init_with_default_template(self):
        view = ContactUs()
        assert view.template == "contact/contact.html"
        assert view.attach_eligiblity_data is False

    def test_init_with_custom_template(self):
        custom_template = "custom/template.html"
        view = ContactUs(template=custom_template)
        assert view.template == custom_template
        assert view.attach_eligiblity_data is False

    def test_init_with_attach_eligibility_data(self):
        view = ContactUs(attach_eligiblity_data=True)
        assert view.template == "contact/contact.html"
        assert view.attach_eligiblity_data is True

    @patch("app.contact.views.ContactUsForm")
    @patch("app.contact.views.MeansTest")
    @patch("app.contact.views.render_template")
    def test_get_request(self, mock_render_template, mock_means_test, mock_form, app):
        mock_form_instance = MagicMock()
        mock_form.return_value = mock_form_instance
        mock_form_instance.validate_on_submit.return_value = False

        mock_means_test_instance = MagicMock()
        mock_means_test.return_value = mock_means_test_instance
        mock_form_progress = {"step": "Review", "percentage_complete": 100}
        mock_means_test_instance.get_form_progress.return_value = mock_form_progress

        with app.app_context():
            view = ContactUs()
            view.dispatch_request()

            mock_render_template.assert_called_once_with(
                "contact/contact.html",
                form=mock_form_instance,
                form_progress=mock_form_progress,
            )

    @patch("app.contact.views.ContactUsForm")
    @patch("app.contact.views.redirect")
    @patch("app.contact.views.cla_backend")
    @patch("app.contact.views.notify")
    @patch.object(ContactUs, "_append_notes_to_eligibility_check")
    def test_post_request_success(
        self,
        mock_append_notes,
        mock_notify,
        mock_cla_backend,
        mock_redirect,
        mock_form,
        client,
    ):
        mock_form_instance = MagicMock()
        mock_form.return_value = mock_form_instance
        mock_form_instance.validate_on_submit.return_value = True
        mock_form_instance.get_payload.return_value = {"case_details": "test"}
        mock_form_instance.get_callback_time.return_value = "2025-01-01 12:00"
        mock_form_instance.get_email.return_value = "test@example.com"
        mock_form_instance.data = {
            "contact_type": "callback",
            "full_name": "John Doe",
            "third_party_full_name": None,
            "contact_number": "07777777777",
            "third_party_contact_number": None,
            "extra_notes": "Some notes",
        }

        mock_cla_backend.post_case.return_value = {"reference": "AB-1234-5678"}

        view = ContactUs()
        view.dispatch_request()

        mock_cla_backend.post_case.assert_called_once()
        mock_append_notes.assert_called_once_with("Some notes")
        mock_notify.create_and_send_confirmation_email.assert_called_once()
        mock_redirect.assert_called_once_with(url_for("contact.confirmation"))

    @patch("app.contact.views.ContactUsForm")
    @patch("app.contact.views.render_template")
    @patch.object(MeansTest, "get_form_progress")
    def test_post_request_validation_failure(
        self, mock_means_test, mock_render_template, mock_form, app
    ):
        mock_form_instance = MagicMock()
        mock_form.return_value = mock_form_instance
        mock_form_instance.validate_on_submit.return_value = False

        mock_means_test.return_value = {"step": "Review", "percentage_complete": 100}

        with app.app_context():
            # Call the view
            view = ContactUs()
            view.dispatch_request()

            mock_render_template.assert_called_once_with(
                "contact/contact.html",
                form=mock_form_instance,
                form_progress={"step": "Review", "percentage_complete": 100},
            )

    @patch("app.contact.views.render_template")
    @patch.object(MeansTest, "get_form_progress")
    def test_attach_rfc_to_case(
        self, mock_get_form_progress, mock_render_template, app, client
    ):
        with client.session_transaction() as session:
            session[ReasonsForContactingForm.MODEL_REF_SESSION_KEY] = "1234"

        form_data = {
            "full_name": "Test User",
            "contact_type": "call",
            "address_finder": "",
            "other_language": "",
        }

        with (
            patch("app.contact.forms.cla_backend"),
            patch(
                "app.contact.views.cla_backend.post_case",
                return_value={"reference": "AB-1234-5678"},
            ),
            patch.object(ContactUs, "_attach_rfc_to_case") as mock_attach_rfc_to_case,
        ):
            client.post("/contact-us", data=form_data)

            mock_attach_rfc_to_case.assert_called_once_with("AB-1234-5678", "1234")

    @patch("app.contact.views.update_means_test")
    def test_append_notes_to_eligibility_check_with_valid_notes(
        self, mock_update_means_test, app, client
    ):
        notes_data = "User notes"

        view = ContactUs()
        view._append_notes_to_eligibility_check(notes_data)

        mock_update_means_test.assert_called_once()
        eligibility_check = mock_update_means_test.mock_calls[0][1][0]
        assert "notes" in eligibility_check
        assert eligibility_check["notes"] == "User problem:\nUser notes"

    @patch("app.contact.views.update_means_test")
    def test_append_notes_to_eligibility_check_with_empty_notes(
        self, mock_update_means_test, app, client
    ):
        # Test with empty string
        view = ContactUs()
        view._append_notes_to_eligibility_check("")

        mock_update_means_test.assert_not_called()

        # Test with None
        view._append_notes_to_eligibility_check(None)

        mock_update_means_test.assert_not_called()

    @patch("app.contact.views.cla_backend.update_reasons_for_contacting")
    def test_attaching_rfc_to_case(self, mock_update_rfc, app, client):
        with client.session_transaction() as session:
            session[ReasonsForContactingForm.MODEL_REF_SESSION_KEY] = "1234"

        case_ref = "AB-1234-5678"
        rfc_ref = "1234"

        ContactUs._attach_rfc_to_case(case_ref, rfc_ref)

        # Verify behavior
        mock_update_rfc.assert_called_once_with(
            "1234",  # Value from mock_session.__getitem__
            payload={"case": case_ref},
        )


class TestFastTrackedContactUsView:
    @patch("app.contact.views.ContactUs.dispatch_request", return_value=None)
    @patch(
        "app.contact.views.FastTrackedContactUs.fast_tracked",
        return_value=(False, None),
    )
    def test_dispatch_request_failure(
        self, mock_fast_tracked, mock_dispatch_request, app
    ):
        with app.app_context():
            view = FastTrackedContactUs()
            response = view.dispatch_request()
            assert response.status_code == 302
            assert response.location == url_for("main.session_expired")
            assert mock_dispatch_request.called is False

    @patch("app.contact.views.ContactUs.dispatch_request", return_value=None)
    @patch(
        "app.contact.views.FastTrackedContactUs.fast_tracked", return_value=(True, None)
    )
    def test_dispatch_request_success(
        self, mock_fast_tracked, mock_dispatch_request, app
    ):
        with app.app_context():
            view = FastTrackedContactUs()
            view.dispatch_request()
            assert mock_dispatch_request.called is True

    @patch("app.contact.views.ContactUs.get_payload_from_form", return_value={})
    @patch(
        "app.contact.views.FastTrackedContactUs.fast_tracked",
        return_value=(True, FinancialAssessmentReason.HARM),
    )
    def test_get_payload_from_form_success(
        self, mock_fast_tracked, mock_super_get_payload_from_form, app
    ):
        with app.app_context():
            view = FastTrackedContactUs()
            payload = view.get_payload_from_form(FlaskForm())
            assert (
                payload["financial_assessment_reason"] == FinancialAssessmentReason.HARM
            )
            assert (
                payload["financial_assessment_status"]
                == FinancialAssessmentStatus.FAST_TRACKING
            )

    @patch("app.contact.views.ContactUs.get_payload_from_form", return_value={})
    @patch(
        "app.contact.views.FastTrackedContactUs.fast_tracked",
        return_value=(False, None),
    )
    def test_get_payload_from_form_failure(
        self, mock_fast_tracked, mock_super_get_payload_from_form, app
    ):
        with app.app_context():
            view = FastTrackedContactUs()
            payload = view.get_payload_from_form(FlaskForm())
            assert "financial_assessment_reason" not in payload
            assert "financial_assessment_status" not in payload

    def test_fast_tracked_no_condition(self, app, client):
        with app.app_context():
            with patch.object(
                Session, "category", new_callable=PropertyMock
            ) as mock_category:
                mock_category.return_value = DOMESTIC_ABUSE.sub.problems_with_neighbours
                view = FastTrackedContactUs()
                is_fast_tracked, fast_track_reason = view.fast_tracked()
                assert is_fast_tracked is True
                assert fast_track_reason == FinancialAssessmentReason.MORE_INFO_REQUIRED

    def test_fast_tracked_condition_failure(self, app, client):
        with app.app_context():
            with patch.object(
                Session, "category_answers", new_callable=PropertyMock
            ) as mock_category_answers:
                mock_category_answers.return_value = [
                    CategoryAnswer(
                        question="Find problems covered by legal aid",
                        answer_value=DOMESTIC_ABUSE.code,
                        answer_label=DOMESTIC_ABUSE.title,
                        next_page="categories.index",
                        question_page="categories.domestic_abuse.landing",
                        category=DOMESTIC_ABUSE,
                    ),
                    CategoryAnswer(
                        question="Are you worried about someone's safety?",
                        answer_value="no",
                        answer_label="No",
                        next_page="categories.index",
                        question_page="categories.domestic_abuse.landing",
                        category=DOMESTIC_ABUSE.sub.problems_with_ex_partner,
                    ),
                ]

                view = FastTrackedContactUs()
                is_fast_tracked, fast_track_reason = view.fast_tracked()
                assert is_fast_tracked is False
                assert fast_track_reason is None

    def test_fast_tracked_condition_success(self, app, client):
        with app.app_context():
            with patch.object(
                Session, "category_answers", new_callable=PropertyMock
            ) as mock_category_answers:
                mock_category_answers.return_value = [
                    CategoryAnswer(
                        question="Find problems covered by legal aid",
                        answer_value=DOMESTIC_ABUSE.code,
                        answer_label=DOMESTIC_ABUSE.title,
                        next_page="categories.index",
                        question_page="categories.domestic_abuse.landing",
                        category=DOMESTIC_ABUSE,
                    ),
                    CategoryAnswer(
                        question="Are you worried about someone's safety?",
                        answer_value="yes",
                        answer_label="Yes",
                        next_page="categories.index",
                        question_page="categories.domestic_abuse.landing",
                        category=DOMESTIC_ABUSE.sub.problems_with_ex_partner,
                    ),
                ]

                view = FastTrackedContactUs()
                is_fast_tracked, fast_track_reason = view.fast_tracked()
                assert is_fast_tracked is True
                assert fast_track_reason == FinancialAssessmentReason.HARM


def test_eligible_view_success(app):
    with app.app_context():
        with patch("app.contact.urls.is_eligible") as mock_is_eligible:
            mock_is_eligible.return_value = EligibilityState.YES
            view = EligibleContactUsPage()
            with patch.object(
                Session,
                "ec_reference",
                return_value="5ae7d8ba-daf2-471f-a082-7aaec590e83b",
            ):
                with patch(
                    "app.contact.views.ContactUs.dispatch_request"
                ) as mock_super_dispatch_request:
                    view.dispatch_request()
                    assert mock_super_dispatch_request.called is True


def test_eligible_view_failure(app):
    with app.app_context():
        with patch("app.contact.urls.is_eligible") as mock_is_eligible:
            mock_is_eligible.return_value = EligibilityState.UNKNOWN
            view = EligibleContactUsPage()
            with patch.object(
                Session,
                "ec_reference",
                return_value="5ae7d8ba-daf2-471f-a082-7aaec590e83b",
            ):
                response = view.dispatch_request()
                assert response.status_code == 302
                assert response.location == url_for("main.session_expired")


def test_eligible_view_failure_no_ec_reference(app):
    with app.app_context():
        with patch("app.contact.urls.is_eligible") as mock_is_eligible:
            mock_is_eligible.return_value = EligibilityState.YES
            view = EligibleContactUsPage()
            response = view.dispatch_request()
            assert mock_is_eligible.called is False
            assert response.status_code == 302
            assert response.location == url_for("main.session_expired")
