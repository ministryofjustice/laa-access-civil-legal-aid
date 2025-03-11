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
