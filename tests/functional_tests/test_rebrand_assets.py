import pytest
from playwright.sync_api import Page
from flask import url_for


@pytest.mark.usefixtures("live_server")
def test_assets_exists(page: Page):
    regular_assets = [
        {"url": "images/favicon.ico", "content_type": "image"},
        {"url": "images/favicon.svg", "content_type": "image"},
        {"url": "images/govuk-icon-mask.svg", "content_type": "image"},
        {"url": "images/govuk-icon-180.png", "content_type": "image"},
        {"url": "manifest.json", "content_type": "application/json"},
    ]
    for asset in regular_assets:
        asset_url = url_for("static", filename=asset["url"], _external=True)
        response = page.request.get(asset_url)
        assert response.status == 200
        assert asset["content_type"] in response.headers.get("content-type", "")


@pytest.mark.usefixtures("live_server")
def test_rebrand_favicon_exists(page: Page):
    rebrand_assets = [
        {"url": "rebrand/images/favicon.ico", "content_type": "image"},
        {"url": "rebrand/images/favicon.svg", "content_type": "image"},
        {"url": "rebrand/images/govuk-icon-mask.svg", "content_type": "image"},
        {"url": "rebrand/images/govuk-icon-180.png", "content_type": "image"},
        {"url": "rebrand/manifest.json", "content_type": "application/json"},
    ]
    for asset in rebrand_assets:
        asset_url = url_for("static", filename=asset["url"], _external=True)
        response = page.request.get(asset_url)
        assert response.status == 200
        assert asset["content_type"] in response.headers.get("content-type", "")
