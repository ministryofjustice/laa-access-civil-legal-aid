import pytest


@pytest.mark.parametrize(
    "endpoint",
    [
        "/",
        "/children-families-relationships",
        "/cookies",
        "/assets/images/favicon.svg",
        "/assets/scripts.js",
        "/assets/styles.css",
        "/404-page",
        "/service-unavailable",
    ],
)
def test_noindex_header_on_routes(client, endpoint):
    response = client.get(endpoint)
    assert response.headers.get("X-Robots-Tag") == "noindex"


def est_no_cache_headers(client):
    response = client.get("/find-your-problem")

    assert response.status_code == 200
    assert (
        response.headers.get("Cache-Control")
        == "no-store, no-cache, must-revalidate, max-age=0"
    )
    assert response.headers.get("Pragma") == "no-cache"
    assert response.headers.get("Expires") == "0"
