import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, session
from app.contact.notify.api import NotifyEmailOrchestrator


class TestNotifyEmailOrchestrator(unittest.TestCase):
    def setUp(self):
        """Set up a test Flask app context"""
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["EMAIL_ORCHESTRATOR_URL"] = "https://email.orchestrator/"
        self.app.secret_key = "test_secret_key"
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        """Clean up app context"""
        self.ctx.pop()

    def test_orchestrator_initialization(self):
        """Test NotifyEmailOrchestrator initializes correctly"""
        orchestrator = NotifyEmailOrchestrator()
        self.assertEqual(orchestrator.base_url, "https://email.orchestrator/")
        self.assertEqual(orchestrator.endpoint, "email")

    def test_orchestrator_url(self):
        """Test URL formation for NotifyEmailOrchestrator"""
        orchestrator = NotifyEmailOrchestrator()
        self.assertEqual(orchestrator.url(), "https://email.orchestrator/email")

    @patch("requests.post")
    def test_send_email_success(self, mock_post):
        """Test successful email sending"""
        self.app.config["TESTING"] = False
        self.app.config["EMAIL_ORCHESTRATOR_URL"] = "https://fake-orchestrator.com"

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        orchestrator = NotifyEmailOrchestrator()
        result = orchestrator.send_email(
            "test@example.com", "template123", {"name": "Test"}
        )

        mock_post.assert_called_once()
        self.assertTrue(result)

    @patch("requests.post")
    def test_send_email_failure(self, mock_post):
        """Test email sending failure"""
        self.app.config["TESTING"] = False
        self.app.config["EMAIL_ORCHESTRATOR_URL"] = "https://fake-orchestrator.com"

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = Exception("Error")
        mock_post.return_value = mock_response

        orchestrator = NotifyEmailOrchestrator()
        with self.assertRaises(Exception):
            orchestrator.send_email("test@example.com", "template123", {"name": "Test"})

        mock_post.assert_called_once()

    @patch("app.contact.notify.api.get_locale", return_value="en")
    @patch(
        "app.contact.notify.api.GOVUK_NOTIFY_TEMPLATES",
        new_callable=lambda: {
            "PUBLIC_CONFIRMATION_EMAIL_CALLBACK_REQUESTED_THIRDPARTY": {
                "en": "template_id_1"
            },
            "PUBLIC_CONFIRMATION_EMAIL_CALLBACK_REQUESTED": {"en": "template_id_2"},
            "PUBLIC_CONFIRMATION_NO_CALLBACK": {"en": "template_id_3"},
            "PUBLIC_CALLBACK_NOT_REQUESTED": {"en": "template_id_4"},
            "PUBLIC_CALLBACK_WITH_NUMBER": {"en": "template_id_5"},
            "PUBLIC_CALLBACK_THIRD_PARTY": {"en": "template_id_6"},
        },
    )
    def test_generate_confirmation_email_data(self, mock_templates, mock_locale):
        """Test generating confirmation email data"""
        with self.app.test_request_context():
            session["case_reference"] = "ABC123"
            session["callback_requested"] = True
            session["contact_type"] = "thirdparty"
            session["callback_time"] = "2025-02-21 10:00 AM"

            data = {
                "email": "user@example.com",
                "full_name": "John Doe",
                "thirdparty_full_name": "Jane Doe",
                "contact_number": "123456789",
                "case_ref": "AB12345",
            }

            orchestrator = NotifyEmailOrchestrator()
            email_address, template_id, personalisation = (
                orchestrator.generate_confirmation_email_data(data)
            )

            self.assertEqual(email_address, "user@example.com")
            self.assertIn("full_name", personalisation)
            self.assertIn("case_reference", personalisation)
            self.assertIn("date_time", personalisation)

    @patch.object(NotifyEmailOrchestrator, "send_email")
    @patch("app.contact.notify.api.get_locale", return_value="en")
    @patch(
        "app.contact.notify.api.GOVUK_NOTIFY_TEMPLATES",
        new_callable=lambda: {
            "PUBLIC_CONFIRMATION_EMAIL_CALLBACK_REQUESTED_THIRDPARTY": {
                "en": "template_id_1"
            },
            "PUBLIC_CONFIRMATION_EMAIL_CALLBACK_REQUESTED": {"en": "template_id_2"},
            "PUBLIC_CONFIRMATION_NO_CALLBACK": {"en": "template_id_3"},
            "PUBLIC_CALLBACK_NOT_REQUESTED": {"en": "template_id_4"},
            "PUBLIC_CALLBACK_WITH_NUMBER": {"en": "template_id_5"},
            "PUBLIC_CALLBACK_THIRD_PARTY": {"en": "template_id_6"},
        },
    )
    def test_create_and_send_confirmation_email(
        self, mock_templates, mock_locale, mock_send_email
    ):
        """Test create_and_send_confirmation_email function"""
        with self.app.test_request_context():
            session["case_reference"] = "ABC123"
            session["callback_requested"] = False
            session["contact_type"] = "email"
            session["callback_time"] = "2025-02-21 10:00 AM"

            data = {
                "email": "user@example.com",
                "full_name": "John Doe",
                "thirdparty_full_name": "Jane Doe",
                "contact_number": "123456789",
            }

            mock_send_email.return_value = True
            govuk_notify = NotifyEmailOrchestrator()

            NotifyEmailOrchestrator.create_and_send_confirmation_email(
                govuk_notify, data
            )
            mock_send_email.assert_called_once()
