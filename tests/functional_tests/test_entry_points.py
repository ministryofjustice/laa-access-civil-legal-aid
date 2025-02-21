from playwright.sync_api import Page, expect
import pytest
from flask import url_for


@pytest.mark.usefixtures("live_server")
def test_start_route(page: Page):
    url = url_for("main.start", _external=True)
    assert url.endswith("/start"), url
    page.goto(url)
    expect(
        page.get_by_role("heading", name="Find problems covered by legal aid")
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_start_route_welsh(page: Page):
    url = url_for("main.start", locale="cy_GB", _external=True)
    assert url.endswith("/start?locale=cy_GB"), url
    page.goto(url)
    locale = page.locator("html").get_attribute("lang")
    assert locale == "cy", f"Expected 'cy' but got {locale}"


@pytest.mark.usefixtures("live_server")
def test_bsl_route(page: Page):
    url = url_for("main.bsl_start", _external=True)
    assert url.endswith("/bsl-start"), url
    page.goto(url)
    expect(
        page.get_by_role("heading", name="Contact Civil Legal Advice")
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_bsl_route_welsh(page: Page):
    url = url_for("main.bsl_start", locale="cy_GB", _external=True)
    assert url.endswith("/bsl-start?locale=cy_GB"), url
    page.goto(url)
    locale = page.locator("html").get_attribute("lang")
    assert locale == "cy", f"Expected 'cy' but got {locale}"
