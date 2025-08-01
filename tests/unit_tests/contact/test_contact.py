import pytest
from unittest.mock import patch
from flask import request, session, current_app
from wtforms.fields.choices import SelectField
from app.api import cla_backend, BackendAPIClient
from app.contact.forms import ReasonsForContactingForm, ContactUsForm
from app.contact.helpers import format_callback_time
import requests
from datetime import datetime
from app.contact.address_finder.widgets import AddressLookup, FormattedAddressLookup
from wtforms import Form, StringField
from wtforms.validators import ValidationError, StopValidation
from app.contact.validators import ValidateDayTime
from freezegun import freeze_time


def test_post_reasons_for_contacting_success(mocker, app):
    with app.app_context():
        mock_post = mocker.patch.object(cla_backend, "post")

        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        response = cla_backend.post_reasons_for_contacting(payload={"key": "value"})

        mock_post.assert_called_once_with("checker/api/v1/reasons_for_contacting/", json={"key": "value"})
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


class MockForm(Form):
    day = SelectField(choices=[])
    time = SelectField(choices=[])
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
@patch.object(BackendAPIClient, "get")
@patch("app.api.datetime")
def test_get_time_slots(mock_datetime, mock_get, api_client, app):
    """Test get_time_slots correctly formats slots"""
    mock_datetime.today.return_value = datetime(2025, 3, 1)
    mock_datetime.strptime.side_effect = lambda *args, **kw: datetime.strptime(*args, **kw)

    mock_get.return_value = {
        "slots": [
            "2025-03-01T09:00:00",
            "2025-03-01T09:30:00",
            "2025-03-02T10:00:00",
        ]
    }

    with app.app_context():
        result = api_client.get_time_slots(num_days=8, is_third_party_callback=False)

    expected = [
        datetime(2025, 3, 1, 9, 0),
        datetime(2025, 3, 1, 9, 30),
        datetime(2025, 3, 2, 10, 0),
    ]

    assert result == expected
    mock_get.assert_called_once_with(
        "checker/api/v1/callback_time_slots/",
        params={"third_party_callback": False, "num_days": 8},
    )


@patch.object(BackendAPIClient, "post")
def test_post_case(mock_post, api_client, app):
    """Test post_case makes correct API call and updates session"""
    mock_post.return_value = {"reference": "ABC123"}
    payload = {"test": "data"}

    with app.test_request_context():
        session.ec_reference = "elig123"
        api_client.post_case(payload=payload)

        expected_payload = {
            "test": "data",
            "eligibility_check": "elig123",
        }
        mock_post.assert_called_once_with("checker/api/v1/case", json=expected_payload)


@patch.object(BackendAPIClient, "patch")
def test_update_reasons_for_contacting(mock_patch, api_client, app):
    """Test update_reasons_for_contacting makes correct API call"""
    mock_patch.return_value = {"success": True}
    reference = "ABC123"
    payload = {"reason": "test_reason"}

    with app.test_request_context():
        response = api_client.update_reasons_for_contacting(reference, payload=payload)

    mock_patch.assert_called_once_with(f"checker/api/v1/reasons_for_contacting/{reference}", json=payload)
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
    mock_get.return_value.json.return_value = {"results": [{"DPA": {"POSTCODE": "SW1A 1AA"}}]}

    results = address_lookup.by_postcode("SW1A 1AA")
    assert results == [{"DPA": {"POSTCODE": "SW1A 1AA"}}]
    mock_get.assert_called_once_with(
        "https://api.os.uk/search/places/v1/postcode",
        params={
            "postcode": "SW1A 1AA",
            "key": current_app.config["OS_PLACES_API_KEY"],
            "output_srs": "WGS84",  # Specifies the coordinate reference system (WGS84 is a global standard)
            "dataset": "DPA",  # Specifies the dataset to query ("DPA" stands for "Definitive Postcode Address")
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
    mock_by_postcode.return_value = [{"DPA": {"POSTCODE": "SW1A 1AA", "POST_TOWN": "London"}}]
    results = formatted_address_lookup.by_postcode("SW1A 1AA")
    assert results == ["London\nSW1A 1AA"]


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
        (
            "invalid-day",
            "1000",
            ValidationError,
            "Can not schedule a callback at the requested time",
        ),
        ("", "1000", StopValidation, None),
    ],
)
def test_validate_day_time(day, time, expected_exception, expected_message):
    """Test validation of time slots against available slots."""

    form = MockForm()
    form.day.data = day
    form.time.data = time

    validator = ValidateDayTime(day_field="day")

    if expected_exception is StopValidation:
        with pytest.raises(StopValidation):
            validator(form, form.time)
    elif expected_exception is ValidationError:
        with pytest.raises(ValidationError) as context:
            validator(form, form.time)
        assert str(context.value) == expected_message
    elif not expected_exception:
        validator(form, form.time)


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
    callback_time = dummy.get_callback_time()
    assert callback_time is None


# Test get payload
class DummyPayload:
    def __init__(self, data):
        self.data = data
        self.contact_type = self

    def get_callback_time(self):
        return datetime(2024, 2, 24, 14, 30)

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
            "other_language": "english",
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
@patch("app.contact.forms.cla_backend")
def test_get_email(app, client):
    # Test when "email" is in the data
    form_with_email = ContactUsForm(data={"email": "test@example.com"})
    assert form_with_email.get_email() == "test@example.com"

    # Test when "bsl_email" is in the data but "email" is not
    form_with_bsl_email = ContactUsForm(data={"bsl_email": "test_bsl@example.com"})
    assert form_with_bsl_email.get_email() == "test_bsl@example.com"

    # Test when neither "email" nor "bsl_email" are in the data
    form_with_no_email = ContactUsForm(data={})
    assert form_with_no_email.get_email() is None


class TestCallbackTimeFunctions:
    @patch("app.contact.forms.cla_backend")
    def test_get_callback_time_no_callback(self, app, client):
        form_data = {"contact_type": "email"}
        form = ContactUsForm(data=form_data)
        result = form.get_callback_time()
        assert result is None

    @patch("app.contact.forms.cla_backend")
    def test_get_callback_time_call_today(self, app, client):
        form_data = {
            "contact_type": "callback",
            "time_to_call": "Call today",
            "call_today_time": "1430",
        }
        form = ContactUsForm(data=form_data)

        with freeze_time("2025-02-26"):
            result = form.get_callback_time()

            expected = datetime(2025, 2, 26, 14, 30)
            assert result == expected

    @patch("app.contact.forms.cla_backend")
    def test_get_callback_time_call_another_day(self, app, client):
        form_data = {
            "contact_type": "callback",
            "time_to_call": "Call on another day",
            "call_another_day": "2025-02-26",
            "call_another_time": "1000",
        }
        form = ContactUsForm(data=form_data)

        result = form.get_callback_time()

        expected = datetime(2025, 2, 26, 10, 0)
        assert result == expected

    @patch("app.contact.forms.cla_backend")
    def test_get_callback_time_thirdparty(self, app, client):
        form_data = {
            "contact_type": "thirdparty",
            "thirdparty_time_to_call": "Call on another day",
            "thirdparty_call_another_day": "2025-05-19",
            "thirdparty_call_another_time": "1600",
        }
        form = ContactUsForm(data=form_data)

        result = form.get_callback_time()

        expected = datetime(2025, 5, 19, 16, 0)
        assert result == expected

    @patch("app.contact.forms.cla_backend")
    def test_get_callback_time_invalid_selection(self, app, client):
        form_data = {
            "contact_type": "callback",
            "time_to_call": "Invalid option",
        }
        form = ContactUsForm(data=form_data)

        result = form.get_callback_time()
        assert result is None

    @patch("app.contact.forms.cla_backend")
    def test_format_callback_time_none_input(self, app, client):
        result = format_callback_time(None)
        assert result is None

    @patch("app.contact.forms.cla_backend")
    def test_format_callback_time_invalid_input(self, app, client):
        result = format_callback_time("not a datetime")
        assert result is None

    @patch("app.contact.forms.cla_backend")
    def test_format_callback_time_valid(self, app, client):
        test_time = datetime(2024, 1, 1, 9, 0)
        result = format_callback_time(test_time)
        assert result == "Monday, 1 January at 09:00 - 09:30"

    @patch("app.contact.forms.cla_backend")
    def test_format_callback_time_with_midnight_crossing(self, app, client):
        test_time = datetime(2024, 1, 1, 23, 45)
        result = format_callback_time(test_time)
        assert result == "Monday, 1 January at 23:45 - 00:15"
