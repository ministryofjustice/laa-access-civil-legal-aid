import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.contact.notify.api import (
    NotifyEmailOrchestrator,
)


class TestNotifyEmailOrchestrator(unittest.TestCase):
    def setUp(self):
        """Set up a test Flask app context"""
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["EMAIL_ORCHESTRATOR_URL"] = "https://email.orchestrator/"
        self.client = self.app.test_client()

    def test_orchestrator_initialization(self):
        """Test NotifyEmailOrchestrator initializes correctly"""
        with self.app.app_context():
            orchestrator = NotifyEmailOrchestrator()
            self.assertEqual(orchestrator.base_url, "https://email.orchestrator/")
            self.assertEqual(orchestrator.endpoint, "email")

    def test_orchestrator_url(self):
        """Test URL formation for NotifyEmailOrchestrator"""
        with self.app.app_context():
            orchestrator = NotifyEmailOrchestrator()
            self.assertEqual(orchestrator.url(), "https://email.orchestrator/email")

    @patch("requests.post")
    def test_send_email_success(self, mock_post):
        """Test successful email sending"""
        app = Flask(__name__)
        app.config["TESTING"] = False
        app.config["EMAIL_ORCHESTRATOR_URL"] = "https://fake-orchestrator.com"

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        with app.app_context():
            orchestrator = NotifyEmailOrchestrator()
            orchestrator.send_email("test@example.com", "template123", {"name": "Test"})

        # Ensure post request was made once
        mock_post.assert_called_once()
