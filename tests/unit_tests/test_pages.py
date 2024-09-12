
def test_set_locale(app, client):
    response = client.get("/locale/cy", headers={"referer": "http://localhost/privacy"})
    assert response.status_code == 302
    assert response.headers["location"] == "/privacy"
    cookies = response.headers["Set-Cookie"].split(";")
    assert "locale=cy" in cookies, "Could not find locale cookie"


def test_set_locale_invalid(app, client):
    response = client.get("/locale/de", headers={"referer": "http://localhost/privacy"})
    assert response.status_code == 404, f"Expecting 404 got {response.status_code}"


def test_maintenance_page_on(app, client):
    app.config["MAINTENANCE_MODE"] = True
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["location"] == "/maintenance-mode"
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 503
    assert response.request.path == "/maintenance-mode"


def test_maintenance_page_off(app, client):
    app.config["MAINTENANCE_MODE"] = False
    response = client.get("/maintenance-mode", follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/"
