from unittest.mock import patch
from flask import url_for, current_app
import pytest
import json


def test_set_locale(app, client):
    response = client.get("/locale/cy", headers={"referer": "http://localhost/privacy"})
    assert response.status_code == 302
    assert response.headers["location"] == "/privacy"
    cookies = response.headers["Set-Cookie"].split(";")
    assert "locale=cy" in cookies, "Could not find locale cookie"


def test_set_locale_invalid(app, client):
    response = client.get("/locale/de", headers={"referer": "http://localhost/privacy"})
    assert response.status_code == 404, f"Expecting 404 got {response.status_code}"


def test_service_unavailable_on(app, client):
    app.config["SERVICE_UNAVAILABLE"] = True
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["location"] == "/service-unavailable"
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 503
    assert response.request.path == "/service-unavailable"


@pytest.mark.parametrize(
    "resource_path",
    ["/assets/styles.css", "/assets/scripts.js", "/assets/images/govuk-crest.png"],
)
def test_service_unavailable_static_assets(app, client, resource_path):
    app.config["SERVICE_UNAVAILABLE"] = True
    response = client.get(resource_path)
    assert response.status_code != 503
    assert response.status_code in [
        200,
        404,
    ]  # Allow 404 as these assets are not served by the test app
    assert response.request.path == resource_path


def test_service_unavailable_off(app, client):
    app.config["SERVICE_UNAVAILABLE"] = False
    response = client.get("/service-unavailable", follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/find-your-problem"


def test_header_link_clears_session(app, client):
    with client.session_transaction() as session:
        session["test"] = "test"

    client.get("/")

    with client.session_transaction() as session:
        assert "test" not in session


@patch("app.main.routes.render_template")
def test_privacy_template(mock_render_template, client):
    response = client.get("/privacy")
    assert response.status_code == 200
    mock_render_template.assert_called_once_with(
        "main/privacy.html",
        govukRebrand=current_app.config.get("GOVUK_REBRAND"),
    )


@patch("app.main.routes.render_template")
def test_online_safety_template(mock_render_template, client):
    response = client.get("/online-safety")
    assert response.status_code == 200
    mock_render_template.assert_called_once_with(
        "main/online-safety.html",
        govukRebrand=current_app.config.get("GOVUK_REBRAND"),
    )


def test_index_redirects_to_govuk(app, client):
    app.config["ENVIRONMENT"] = "production"
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["location"] == "https://www.gov.uk/check-legal-aid"


def test_index_redirects_to_welsh_govuk(app, client):
    client.set_cookie("locale", "cy")
    app.config["ENVIRONMENT"] = "production"
    response = client.get("/")
    assert response.status_code == 302
    assert (
        response.headers["location"]
        == "https://www.gov.uk/gwirio-os-ydych-yn-gymwys-i-gael-cymorth-cyfreithiol"
    )


def get_cookies_policy(headers: list) -> dict:
    cookies_policy = {}
    for header in headers:
        if "cookies_policy" in header:
            cookie: str = (
                header.split("cookies_policy=")
                .pop()
                .split(";")[0]
                .replace('"{', "{")
                .replace('}"', "}")
            )
            cookie = cookie.replace('\\"', '"').replace("\\054", ",")
            cookies_policy = json.loads(cookie)
            break
    return cookies_policy


def test_cookies_page(app, client):
    with app.test_request_context():
        cookie_policy = {"functional": "yes", "analytics": "yes"}
        response = client.post(
            url_for("main.cookies", _external=True), data=cookie_policy
        )
        assert response.status_code == 200
        assert cookie_policy == get_cookies_policy(
            response.headers.getlist("Set-Cookie")
        )


def test_cookies_page_remove_ga_cookies(app, client):
    with app.test_request_context():
        cookie_policy = {"functional": "no", "analytics": "no"}
        client.set_cookie("_ga", "test_value")
        client.set_cookie("_ga_27837237374", "test_value2")
        client.set_cookie("gtm_anon_id", "test_value3")
        response = client.post(
            url_for("main.cookies", _external=True), data=cookie_policy
        )
        assert response.status_code == 200
        assert cookie_policy == get_cookies_policy(
            response.headers.getlist("Set-Cookie")
        )
        assert "_ga=; Expires=Thu, 01 Jan 1970 00:00:00" in str(
            response.headers.getlist("Set-Cookie")
        )
        assert "_ga_27837237374=; Expires=Thu, 01 Jan 1970 00:00:00" in str(
            response.headers.getlist("Set-Cookie")
        )
