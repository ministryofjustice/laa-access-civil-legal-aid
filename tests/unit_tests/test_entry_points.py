from flask import url_for


class TestStartRoute:
    def test_start_clears_session(self, app, client):
        with client.session_transaction() as session:
            session["test_key"] = "test_value"

        client.get("/start")

        with client.session_transaction() as session:
            assert "test_key" not in session

    def test_start_redirects_to_categories_index(self, client):
        response = client.get("/start")
        assert response.status_code == 302
        assert response.location == url_for("categories.index")

    def test_start_sets_locale_cookie_when_provided(self, client):
        response = client.get("/start?locale=cy_GB")

        assert response.status_code == 302
        assert response.location == url_for("categories.index")

        cookies = response.headers.getlist("Set-Cookie")
        assert any("locale=cy" in cookie for cookie in cookies)

    def test_start_no_locale_cookie_when_not_provided(self, client):
        response = client.get("/start")

        assert response.status_code == 302

        # Verify no locale cookie is set
        cookies = response.headers.getlist("Set-Cookie")
        assert not any("locale=" in cookie for cookie in cookies)

    def test_start_with_invalid_locale(self, client):
        response = client.get("/start?locale=invalid")
        assert response.status_code == 404


class TestBSLStartRoute:
    def test_bsl_start_clears_session(self, app, client):
        with client.session_transaction() as session:
            session["test_key"] = "test_value"

        client.get("/start-bsl")

        with client.session_transaction() as session:
            assert "test_key" not in session

    def test_bsl_start_redirects_to_contact_us(self, client):
        response = client.get("/start-bsl")
        assert response.status_code == 302
        assert response.location == url_for("contact.contact_us")

    def test_bsl_start_sets_locale_cookie_when_provided(self, client):
        response = client.get("/start-bsl?locale=cy_GB")

        # Verify cookie is set
        cookies = response.headers.getlist("Set-Cookie")
        assert any("locale=cy" in cookie for cookie in cookies)

    def test_bsl_start_no_locale_cookie_when_not_provided(self, client):
        response = client.get("/start-bsl")

        # Verify no locale cookie is set
        cookies = response.headers.getlist("Set-Cookie")
        assert not any("locale=" in cookie for cookie in cookies)

    def test_bsl_start_with_invalid_locale(self, client):
        response = client.get("/start-bsl?locale=invalid")
        assert response.status_code == 404
