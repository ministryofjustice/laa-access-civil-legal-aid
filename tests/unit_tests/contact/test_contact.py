import pytest
from flask import Flask
from app.contact.api import post_reasons_for_contacting


@pytest.fixture
def app():
    """Mocked app with mock backend"""
    app = Flask(__name__)
    app.config["CLA_BACKEND_URL"] = "http://mock-backend"
    return app


def test_post_reasons_for_contacting_success(mocker, app):
    with app.app_context():
        mock_post = mocker.patch("requests.post")

        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        response = post_reasons_for_contacting(payload={"key": "value"})

        mock_post.assert_called_once_with(
            url="http://mock-backend/checker/api/v1/reasons_for_contacting/",
            json={"key": "value"},
        )
        assert response == mock_response
