import pytest
from unittest.mock import patch, Mock
from flask import Flask
from wtforms import Form
from app.means_test.forms.outgoings import PartnerMoneyField, PartnerMoneyIntervalField


@pytest.fixture
def test_app():
    app = Flask(__name__)
    return app


@pytest.fixture
def test_request_context(test_app):
    with test_app.test_request_context():
        yield


@pytest.fixture
def mock_session(test_request_context):
    """Mock the session's get_eligibility method properly."""
    with patch("app.means_test.forms.outgoings.session") as mock_session:
        eligibility_mock = Mock()
        eligibility_mock.has_partner = False  # Default to no partner

        mock_session.get_eligibility = Mock(return_value=eligibility_mock)

        yield mock_session


class TestForm(Form):
    money_field = PartnerMoneyField(
        label="Income",
        description="Single description",
        partner_description="Partner description",
    )
    interval_field = PartnerMoneyIntervalField(hint_text="Hint for single", partner_hint_text="Hint for partners")


def test_description_no_partner(mock_session):
    mock_session.get_eligibility.return_value.has_partner = False
    form = TestForm()
    assert form.money_field.description == "Single description"


def test_description_with_partner(mock_session):
    mock_session.get_eligibility.return_value.has_partner = True
    form = TestForm()
    assert form.money_field.description == "Partner description"


def test_partner_money_field_initialization():
    form = TestForm()
    assert form.money_field._description == "Single description"
    assert form.money_field._partner_description == "Partner description"
