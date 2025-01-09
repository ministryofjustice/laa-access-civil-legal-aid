import pytest
from unittest.mock import patch
from flask import Flask, request
from flask_babel import Babel
from app.api import cla_backend
from app.contact.forms import ReasonsForContactingForm


@pytest.fixture
def app():
    """Mocked app with mock backend"""
    app = Flask(__name__)
    app.config["CLA_BACKEND_URL"] = "http://mock-backend"
    app.config["SECRET_KEY"] = "secret-key"
    Babel(app)
    return app


def test_post_reasons_for_contacting_success(mocker, app):
    with app.app_context():
        mock_post = mocker.patch("requests.post")

        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        response = cla_backend.post_reasons_for_contacting(payload={"key": "value"})

        mock_post.assert_called_once_with(
            url="http://mock-backend/checker/api/v1/reasons_for_contacting/",
            json={"key": "value"},
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
