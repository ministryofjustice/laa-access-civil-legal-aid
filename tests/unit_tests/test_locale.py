import pytest
from flask import Response
from werkzeug.exceptions import NotFound
from app.main.routes import set_locale_cookie
import datetime as dt


@pytest.fixture
def mock_response():
    return Response()


def test_valid_locale(app, mock_response):
    response = set_locale_cookie(mock_response, "en")

    cookie = response.headers.get("Set-Cookie")

    expiry_time = dt.datetime.now() + dt.timedelta(days=30)

    assert "locale=en" in cookie
    assert "Secure" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=Strict" in cookie
    assert "Expires" in cookie
    assert expiry_time.strftime("%a, %d %b %Y %H:%M:%S GMT") in cookie


def test_locale_with_gb_suffix(app, mock_response):
    response = set_locale_cookie(mock_response, "en_GB")
    assert "locale=en" in response.headers.get("Set-Cookie")


def test_invalid_locale(app, mock_response):
    with pytest.raises(NotFound):
        set_locale_cookie(mock_response, "invalid")


def test_none_locale(app, mock_response):
    response = set_locale_cookie(mock_response, None)
    assert response.headers.get("Set-Cookie") is None


def test_empty_string_locale(app, mock_response):
    response = set_locale_cookie(mock_response, "")
    assert response.headers.get("Set-Cookie") is None


def test_non_string_locale(app, mock_response):
    response = set_locale_cookie(mock_response, 123)
    assert response.headers.get("Set-Cookie") is None
