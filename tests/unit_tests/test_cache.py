def test_no_cache_headers(client):
    response = client.get("/find-your-problem")

    assert response.status_code == 200
    assert (
        response.headers.get("Cache-Control")
        == "no-store, no-cache, must-revalidate, max-age=0"
    )
    assert response.headers.get("Pragma") == "no-cache"
    assert response.headers.get("Expires") == "0"
