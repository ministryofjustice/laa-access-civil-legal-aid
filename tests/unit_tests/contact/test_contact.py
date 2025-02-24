import pytest
from unittest.mock import patch
from flask import request, Flask, session
from app.api import cla_backend, BackendAPIClient
from app.contact.forms import ReasonsForContactingForm, ContactUsForm
import requests
from datetime import datetime
from app.contact.address_finder.widgets import AddressLookup, FormattedAddressLookup
from wtforms import Form, StringField, FieldList
from wtforms.validators import ValidationError, StopValidation
from app.contact.validators import ValidateDayTime
from flask_babel import Babel


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


@pytest.fixture
def app():
    """Creates a Flask app with the required configuration."""
    app = Flask(__name__)
    app.config["OS_PLACES_API_KEY"] = "test_api_key"
    app.config["SECRET_KEY"] = "secret_key"
    app.config["LANGUAGES"] = {"en": "English", "cy": "Welsh"}
    app.config["TIMEZONE"] = "Europe/London"
    Babel(app)
    with app.app_context():
        yield app


class MockForm(Form):
    day = FieldList(StringField())
    time = FieldList(StringField())
    email = StringField("Email")
    bsl_email = StringField("BSL Email")

    def get_email(self):
        return self.data.get("email") or self.data.get("bsl_email")

    time_slots = {
        "2025-02-26": [
            ["1000", "10:00am to 10:30am"],
            ["1100", "11:00am to 11:30am"],
            ["1200", "12:00am to 12:30am"],
        ],
        "2025-02-27": [["1400", "14:00am to 14:30am"], ["1500", "15:00am to 15:30am"]],
    }


# Backend API tests
@pytest.fixture
def client(app):
    """Fixture to set up the BackendAPIClient."""
    return BackendAPIClient()


@patch.object(BackendAPIClient, "get")
@patch("app.api.datetime")
def test_get_time_slots(mock_datetime, mock_get, client, app):
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

    with app.app_context():
        result = client.get_time_slots(num_days=8, is_third_party_callback=False)

    expected = {
        "2025-03-01": [
            ["0900", "9:00am to 9:30am"],
            ["0930", "9:30am to 10:00am"],
        ],
        "2025-03-02": [
            ["1000", "10:00am to 10:30am"],
        ],
    }
    assert result == expected
    mock_get.assert_called_once_with(
        "checker/api/v1/callback_time_slots/",
        "?third_party_callback=False&num_days=8",
    )


@patch.object(BackendAPIClient, "post")
def test_post_case(mock_post, client, app):
    """Test post_case makes correct API call and updates session"""
    mock_post.return_value = {"reference": "ABC123"}
    payload = {"test": "data"}

    with app.test_request_context():
        session["ec_reference"] = "elig123"
        client.post_case(payload=payload, attach_eligiblity_data=True)

        expected_payload = {
            "test": "data",
            "eligibility_check": "elig123",
        }
        mock_post.assert_called_once_with("checker/api/v1/case", json=expected_payload)
        assert session["case_reference"] == "ABC123"


@patch.object(BackendAPIClient, "patch")
def test_update_reasons_for_contacting(mock_patch, client, app):
    """Test update_reasons_for_contacting makes correct API call"""
    mock_patch.return_value = {"success": True}
    reference = "ABC123"
    payload = {"reason": "test_reason"}

    with app.test_request_context():
        response = client.update_reasons_for_contacting(reference, payload=payload)

    mock_patch.assert_called_once_with(
        f"checker/api/v1/reasons_for_contacting/{reference}", json=payload
    )
    assert response == {"success": True}


# Test postcode lookup
@pytest.fixture
def address_lookup(app):
    """Fixture to set up AddressLookup within an active Flask app context."""
    with app.app_context():
        yield AddressLookup()


@patch("app.contact.address_finder.widgets.requests.get")
def test_by_postcode_success(mock_get, address_lookup):
    """Test successful address lookup"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "results": [{"DPA": {"POSTCODE": "SW1A 1AA"}}]
    }

    results = address_lookup.by_postcode("SW1A 1AA")
    assert results == [{"DPA": {"POSTCODE": "SW1A 1AA"}}]
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
def test_by_postcode_timeout(mock_get, address_lookup):
    """Test handling of request timeout"""
    results = address_lookup.by_postcode("SW1A 1AA")
    assert results == []


@patch("app.contact.address_finder.widgets.requests.get")
def test_by_postcode_request_exception(mock_get, address_lookup):
    """Test handling of a general request failure"""
    mock_get.side_effect = requests.exceptions.RequestException("API failure")
    results = address_lookup.by_postcode("SW1A 1AA")
    assert results == []


@pytest.fixture
def formatted_address_lookup(app):
    """Fixture to set up FormattedAddressLookup within an active Flask app context."""
    with app.app_context():
        yield FormattedAddressLookup()


@patch.object(AddressLookup, "by_postcode")
def test_by_postcode_formatted(mock_by_postcode, formatted_address_lookup):
    """Test formatted address lookup"""
    mock_by_postcode.return_value = [
        {"DPA": {"POSTCODE": "SW1A 1AA", "POST_TOWN": "London"}}
    ]
    results = formatted_address_lookup.by_postcode("SW1A 1AA")
    assert results == ["London\nSW1A 1AA"]


def test_format_address_from_dpa_result(formatted_address_lookup):
    """Test address formatting"""
    raw_result = {
        "ORGANISATION_NAME": "Big Ben",
        "BUILDING_NUMBER": "10",
        "THOROUGHFARE_NAME": "Downing Street",
        "POST_TOWN": "London",
        "POSTCODE": "sw1a 2aa",
    }
    expected_output = "Big Ben\n10 Downing Street\nLondon\nSW1A 2AA"
    result = formatted_address_lookup.format_address_from_dpa_result(raw_result)
    assert result == expected_output


# Test Contact Validators
@pytest.mark.parametrize(
    "day, time, expected_exception, expected_message",
    [
        ("2025-02-26", "1000", StopValidation, None),  # valid time slot
        (
            "2025-02-26",
            "0930",
            ValidationError,
            "Can not schedule a callback at the requested time",
        ),  # invalid time slot
    ],
)
def test_validate_day_time(day, time, expected_exception, expected_message):
    """Test validation of time slots against available slots."""

    form = MockForm()
    form.day.append_entry(day)
    form.time.append_entry(time)

    validator = ValidateDayTime(day_field="day")

    if expected_exception is StopValidation:
        with pytest.raises(StopValidation):
            validator(form, form.time)
    elif expected_exception is ValidationError:
        with pytest.raises(ValidationError) as context:
            validator(form, form.time)
        assert str(context.value) == expected_message


# Test for time slots functionality
class DummyTimeSlotProvider:
    def __init__(self, time_slots):
        self.time_slots = time_slots

    def get_all_time_slots(self):
        valid_time_slots = set()
        for times in self.time_slots.values():
            for time in times:
                valid_time_slots.add((time[0], time[1]))

        valid_time_slots = list(valid_time_slots)
        sorted_valid_time_slots = sorted(valid_time_slots)

        return sorted_valid_time_slots


def test_get_all_time_slots():
    sample_time_slots = {
        "2025-02-26": [
            ["1000", "10:00am to 10:30am"],
            ["1100", "11:00am to 11:30am"],
            ["1200", "12:00am to 12:30am"],
        ],
        "2025-02-27": [
            ["1400", "14:00am to 14:30am"],
            ["1500", "15:00am to 15:30am"],
        ],
    }

    provider = DummyTimeSlotProvider(sample_time_slots)
    result = provider.get_all_time_slots()

    expected = [
        ("1000", "10:00am to 10:30am"),
        ("1100", "11:00am to 11:30am"),
        ("1200", "12:00am to 12:30am"),
        ("1400", "14:00am to 14:30am"),
        ("1500", "15:00am to 15:30am"),
    ]

    assert result == expected


# Test get callback time
class DummyCallback:
    def __init__(self, data):
        self.data = data

    get_callback_time = ContactUsForm.get_callback_time


def test_get_callback_time_invalid(app):
    """
    Test that get_callback_time returns (None, None) when the contact_type
    is not 'callback' or 'thirdparty'.
    """
    dummy = DummyCallback({"contact_type": "email"})
    iso_time, callback_time = dummy.get_callback_time()
    assert iso_time is None
    assert callback_time is None


# Test get payload
class DummyPayload:
    def __init__(self, data):
        self.data = data
        self.contact_type = self

    def get_callback_time(self):
        return "2024-02-24T14:30:00Z", "Monday, 24 February at 14:30 - 15:00"

    def get_email(self):
        return "test@example.com"

    get_payload = ContactUsForm.get_payload


def test_get_payload_callback(app):
    """Test payload generation for a callback request."""
    dummy = DummyPayload(
        {
            "contact_type": "callback",
            "full_name": "John Doe",
            "post_code": "SW1A 1AA",
            "contact_number": "07123456789",
            "street_address": "10 Downing Street",
            "announce_call_from_cla": True,
            "adaptations": ["bsl_webcam"],
            "other_language": ["english"],
            "other_adaptation": "None",
        }
    )

    payload = dummy.get_payload()

    assert payload["personal_details"]["full_name"] == "John Doe"
    assert payload["personal_details"]["safe_to_contact"] == "SAFE"
    assert payload["callback_type"] == "web_form_self"
    assert payload["adaptation_details"]["bsl_webcam"] is True
    assert payload["adaptation_details"]["language"] == "ENGLISH"


# Test get email
def test_get_email():
    # Test when "email" is in the data
    form_with_email = MockForm(data={"email": "test@example.com"})
    assert form_with_email.get_email() == "test@example.com"

    # Test when "bsl_email" is in the data but "email" is not
    form_with_bsl_email = MockForm(data={"bsl_email": "test_bsl@example.com"})
    assert form_with_bsl_email.get_email() == "test_bsl@example.com"

    # Test when neither "email" nor "bsl_email" are in the data
    form_with_no_email = MockForm(data={})
    assert form_with_no_email.get_email() is None
