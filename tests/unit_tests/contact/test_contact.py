import pytest
from unittest.mock import patch
from flask import request, Flask, session
from app.api import cla_backend
from app.contact.forms import ReasonsForContactingForm
import unittest
from datetime import datetime
from app.api import BackendAPIClient


def test_post_reasons_for_contacting_success(mocker, app):
    with app.app_context():
        mock_post = mocker.patch.object(cla_backend, "post")

        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        response = cla_backend.post_reasons_for_contacting(payload={"key": "value"})

        mock_post.assert_called_once_with(
            "checker/api/v1/reasons_for_contacting/", json={"key": "value"}
        )
        assert response == mock_response


@pytest.fixture
def mock_form(app):
    """Fixture to mock the form object."""
    with app.app_context():
        form = ReasonsForContactingForm()
        form.reasons.data = ["reason1", "reason2"]
        form.referrer.data = "http://example.com"
        return form


def test_api_payload(mock_form):
    """Test the api_payload function."""
    with patch.object(request, "headers", {"User-Agent": "test-agent"}):
        payload = mock_form.api_payload()

    expected_payload = {
        "reasons": [{"category": "reason1"}, {"category": "reason2"}],
        "other_reasons": "",
        "user_agent": "test-agent",
        "referrer": "http://example.com",
    }

    assert payload == expected_payload


class TestBackendAPIClient(unittest.TestCase):
    def setUp(self):
        """Setup Flask app context for session handling"""
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "test_secret"
        self.client = BackendAPIClient()

    @patch.object(BackendAPIClient, "get")
    @patch("app.api.datetime")
    def test_get_time_slots(self, mock_datetime, mock_get):
        """Test get_time_slots correctly formats slots"""
        mock_datetime.today.return_value = datetime(2025, 3, 1)
        mock_datetime.strptime.side_effect = lambda *args, **kw: datetime.strptime(
            *args, **kw
        )

        mock_get.return_value = {
            "slots": [
                "2025-03-01T09:00:00",
                "2025-03-01T09:30:00",
                "2025-03-02T10:00:00",
            ]
        }

        with self.app.app_context():
            result = self.client.get_time_slots(
                num_days=8, is_third_party_callback=False
            )

        expected = {
            "2025-03-01": [
                ["0900", "9:00am to 9:30am"],
                ["0930", "9:30am to 10:00am"],
            ],
            "2025-03-02": [
                ["1000", "10:00am to 10:30am"],
            ],
        }
        self.assertEqual(result, expected)
        mock_get.assert_called_once_with(
            "checker/api/v1/callback_time_slots/",
            "?third_party_callback=False&num_days=8",
        )

    @patch.object(BackendAPIClient, "post")
    def test_post_case(self, mock_post):
        """Test post_case makes correct API call and updates session"""
        mock_post.return_value = {"reference": "ABC123"}
        payload = {"test": "data"}

        with self.app.test_request_context():
            session["gtm_anon_id"] = "anon123"
            session["ec_reference"] = "elig123"
            self.client.post_case(payload=payload, attach_eligiblity_data=True)

            expected_payload = {
                "test": "data",
                "gtm_anon_id": "anon123",
                "eligibility_check": "elig123",
            }
            mock_post.assert_called_once_with(
                "checker/api/v1/case", json=expected_payload
            )
            self.assertEqual(session["reference"], "ABC123")

    @patch.object(BackendAPIClient, "patch")
    def test_update_reasons_for_contacting(self, mock_patch):
        """Test update_reasons_for_contacting makes correct API call"""
        mock_patch.return_value = {"success": True}
        reference = "ABC123"
        payload = {"reason": "test_reason"}

        with self.app.test_request_context():
            response = self.client.update_reasons_for_contacting(
                reference, payload=payload
            )

        mock_patch.assert_called_once_with(
            f"checker/api/v1/reasons_for_contacting/{reference}", json=payload
        )
        self.assertEqual(response, {"success": True})
