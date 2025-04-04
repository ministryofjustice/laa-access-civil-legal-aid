import pytest
from unittest import mock
from wtforms.validators import ValidationError
from flask_babel import gettext as _
from app.means_test.forms.property import (
    PropertyPayload,
    validate_single_main_home,
    PropertyForm,
)
from app.session import Eligibility


def test_property_payload_with_valid_data():
    form_data = {
        "submit": False,
        "is_main_home": True,
        "other_shareholders": False,
        "property_value": 230000,
        "mortgage_remaining": 100000,
        "mortgage_payments": 500,
        "is_rented": True,
        "rent_amount": {
            "per_interval_value": 500,
            "per_interval_value_pounds": 50.0,
            "interval_period": "per_week",
        },
        "in_dispute": False,
        "csrf_token": None,
    }
    expected_property_value = 23000000
    expected_mortgage_remaining = 10000000
    expected_rent = 500
    expected_share = 100

    payload = PropertyPayload(form_data)

    assert payload["value"] == expected_property_value
    assert payload["mortgage_left"] == expected_mortgage_remaining
    assert payload["share"] == expected_share
    assert payload["disputed"] is False
    assert payload["main"]

    rent = payload["rent"]["per_interval_value"]
    assert rent == expected_rent


def test_property_payload_with_missing_rent():
    form_data = {
        "submit": False,
        "is_main_home": True,
        "other_shareholders": False,
        "property_value": 230000,
        "mortgage_remaining": 100000,
        "mortgage_payments": 500,
        "is_rented": True,
        "rent_amount": {
            "per_interval_value": None,
            "per_interval_value_pounds": None,
            "interval_period": None,
        },
        "in_dispute": False,
        "csrf_token": None,
    }

    expected_property_value = 23000000
    expected_mortgage_remaining = 10000000
    expected_rent = {"per_interval_value": None, "interval_period": None}
    expected_share = 100

    payload = PropertyPayload(form_data)

    assert payload["value"] == expected_property_value
    assert payload["mortgage_left"] == expected_mortgage_remaining
    assert payload["share"] == expected_share
    assert payload["disputed"] is False
    assert payload["main"]

    rent = payload["rent"]
    assert rent == expected_rent


class MockForm:
    def __init__(self, properties_data):
        self.properties = MockField(properties_data)


class MockField:
    def __init__(self, data):
        self.data = data


def test_validate_single_main_home_multiple_main_homes():
    """Test with multiple main homes."""
    form_data = [
        {"is_main_home": True},
        {"is_main_home": True},
    ]
    form = MockForm(form_data)

    # Expecting a ValidationError
    with pytest.raises(ValidationError) as errorinfo:
        validate_single_main_home(form, None)

    assert str(errorinfo.value) == _("You can only have 1 main property")


def test_property_add():
    form_data = [{"is_main_home": True}]
    form = MockForm(form_data)

    form.properties.data.append({"is_main_home": False})

    assert len(form.properties.data) == 2
    assert form.properties.data[1]["is_main_home"] is False


def test_property_remove_second():
    form_data = [{"is_main_home": True}, {"is_main_home": False}]
    form = MockForm(form_data)

    form.properties.data.pop(1)

    assert len(form.properties.data) == 1
    assert form.properties.data[0]["is_main_home"]


def test_property_remove_third():
    form_data = [
        {"is_main_home": True},
        {"is_main_home": False},
        {"is_main_home": False},
    ]
    form = MockForm(form_data)

    form.properties.data.pop(2)

    assert len(form.properties.data) == 2
    assert all(isinstance(prop, dict) for prop in form.properties.data)


def test_property_should_show_success(app):
    with app.app_context():
        with mock.patch("app.means_test.forms.property.session") as benefits_session:
            benefits_session.get_eligibility = mock.Mock(
                return_value=Eligibility(forms={"about-you": {"own_property": True}})
            )
            form = PropertyForm()
            assert form.should_show() is True


def test_property_should_show_failure(app):
    with app.app_context():
        with mock.patch("app.means_test.forms.benefits.session") as benefits_session:
            benefits_session.get_eligibility = mock.Mock(
                return_value=Eligibility(forms={"about-you": {"own_property": False}})
            )
            form = PropertyForm()
            assert form.should_show() is False
