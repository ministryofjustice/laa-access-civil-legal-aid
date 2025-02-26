from unittest.mock import patch, MagicMock
from flask import url_for
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
