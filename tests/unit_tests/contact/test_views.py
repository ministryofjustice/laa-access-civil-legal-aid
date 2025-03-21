from unittest.mock import patch, MagicMock
from flask import url_for

from app.contact.forms import ReasonsForContactingForm
from app.contact.views import ContactUs
from app.means_test.views import MeansTest


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
    def test_get_request(self, mock_render_template, mock_means_test, mock_form):
        mock_form_instance = MagicMock()
        mock_form.return_value = mock_form_instance
        mock_form_instance.validate_on_submit.return_value = False

        mock_means_test_instance = MagicMock()
        mock_means_test.return_value = mock_means_test_instance
        mock_form_progress = {"step": "Review", "percentage_complete": 100}
        mock_means_test_instance.get_form_progress.return_value = mock_form_progress

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
        self, mock_means_test, mock_render_template, mock_form
    ):
        mock_form_instance = MagicMock()
        mock_form.return_value = mock_form_instance
        mock_form_instance.validate_on_submit.return_value = False

        mock_means_test.return_value = {"step": "Review", "percentage_complete": 100}

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
