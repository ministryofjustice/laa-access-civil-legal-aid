import pytest


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
    assert response.status_code == 200
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
