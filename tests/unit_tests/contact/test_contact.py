import pytest
from unittest.mock import patch
from flask import request, Flask, session
from app.api import cla_backend
from app.contact.forms import ContactUsForm, ReasonsForContactingForm
import unittest
from unittest import mock
import requests
from datetime import datetime
from app.api import BackendAPIClient
from app.contact.address_finder.widgets import AddressLookup, FormattedAddressLookup
from app import create_app


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


class TestAddressLookup(unittest.TestCase):
    def setUp(self):
        """Set up test instance with mock API key."""
        self.lookup = AddressLookup(key="test_api_key")

    @patch("app.contact.address_finder.widgets.requests.get")
    def test_by_postcode_success(self, mock_get):
        """Test successful address lookup"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "results": [{"DPA": {"POSTCODE": "SW1A 1AA"}}]
        }

        results = self.lookup.by_postcode("SW1A 1AA")
        self.assertEqual(results, [{"DPA": {"POSTCODE": "SW1A 1AA"}}])
        mock_get.assert_called_once_with(
            "https://api.os.uk/search/places/v1/postcode",
            params={
                "postcode": "SW1A 1AA",
                "key": "test_api_key",
                "output_srs": "WGS84",
                "dataset": "DPA",
            },
            timeout=3,
        )

    @patch(
        "app.contact.address_finder.widgets.requests.get",
        side_effect=requests.exceptions.ConnectTimeout,
    )
    def test_by_postcode_timeout(self, mock_get):
        """Test handling of request timeout"""
        results = self.lookup.by_postcode("SW1A 1AA")
        self.assertEqual(results, [])

    @patch("app.contact.address_finder.widgets.requests.get")
    def test_by_postcode_request_exception(self, mock_get):
        """Test handling of a general request failure"""
        mock_get.side_effect = requests.exceptions.RequestException("API failure")
        results = self.lookup.by_postcode("SW1A 1AA")
        self.assertEqual(results, [])


class TestFormattedAddressLookup(unittest.TestCase):
    def setUp(self):
        self.lookup = FormattedAddressLookup(key="test_api_key")

    @patch.object(AddressLookup, "by_postcode")
    def test_by_postcode_formatted(self, mock_by_postcode):
        """Test formatted address lookup"""
        mock_by_postcode.return_value = [
            {"DPA": {"POSTCODE": "SW1A 1AA", "POST_TOWN": "London"}}
        ]

        results = self.lookup.by_postcode("SW1A 1AA")
        self.assertEqual(results, ["London\nSW1A 1AA"])

    def test_format_address_from_dpa_result(self):
        """Test address formatting"""
        raw_result = {
            "ORGANISATION_NAME": "Big Ben",
            "BUILDING_NUMBER": "10",
            "THOROUGHFARE_NAME": "Downing Street",
            "POST_TOWN": "London",
            "POSTCODE": "sw1a 2aa",
        }
        expected_output = "Big Ben\n10 Downing Street\nLondon\nSW1A 2AA"

        result = self.lookup.format_address_from_dpa_result(raw_result)
        self.assertEqual(result, expected_output)


class TestContactUsForm(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_get_callback_time_call_on_another_day(self):
        with mock.patch("requests.get") as mock_get:
            mock_response = mock.Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "time_slots": [
                    {"time": "2025-02-21T14:00:00Z", "availability": "available"}
                ]
            }

            mock_get.return_value = mock_response

            with self.app.test_request_context(
                "/contact",
                method="POST",
                data={
                    "contact_type": "callback",
                    "time_to_call": "Call on another day",
                    "call_another_day": ["2025-02-21"],
                    "call_another_time": ["1400"],
                },
            ):
                form = ContactUsForm()
                iso_time, callback_time = form.get_callback_time()

                self.assertIsNotNone(iso_time)
                self.assertIsNotNone(callback_time)
                self.assertIn("Friday, 21 February at 14:00 - 14:30", callback_time)
