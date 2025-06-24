import json
import uuid
from app.main.gtm import get_gtm_anon_id_from_cookie


def test_get_gtm_anon_id_from_valid_cookie(app, client):
    valid_uuid = str(uuid.uuid4())
    client.set_cookie("gtm_anon_id", valid_uuid)

    with app.test_request_context("/", headers={"Cookie": f"gtm_anon_id={valid_uuid}"}):
        result = get_gtm_anon_id_from_cookie()
        assert result == valid_uuid


def test_get_gtm_anon_id_from_invalid_cookie(app):
    with app.test_request_context(
        "/", headers={"Cookie": "gtm_anon_id=not-a-valid-uuid"}
    ):
        result = get_gtm_anon_id_from_cookie()
        assert result is None


def test_gtm_anon_id_not_set_without_analytics_consent(client):
    client.set_cookie(
        "cookies_policy", json.dumps({"analytics": "no", "functional": "yes"})
    )

    response = client.get("/find-your-problem")
    with client.session_transaction() as sesh:
        assert "gtm_anon_id" not in sesh
    assert "gtm_anon_id" not in response.headers.get("Set-Cookie", "")


def test_gtm_anon_id_set_with_analytics_consent(client):
    client.set_cookie(
        "cookies_policy", json.dumps({"analytics": "yes", "functional": "yes"})
    )

    response = client.get("/find-your-problem")

    with client.session_transaction() as sesh:
        anon_id = sesh.get("gtm_anon_id")
        assert anon_id is not None
        assert isinstance(uuid.UUID(anon_id), uuid.UUID)

    cookies = response.headers.getlist("Set-Cookie")

    assert any("gtm_anon_id=" in cookie for cookie in cookies)
