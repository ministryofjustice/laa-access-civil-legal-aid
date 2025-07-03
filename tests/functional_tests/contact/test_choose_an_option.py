import pytest
from playwright.sync_api import Page, expect
from flask import url_for


@pytest.mark.usefixtures("live_server")
def test_choose_an_option_error(page: Page) -> None:
    page.goto(url_for("contact_us.choose_an_option", _external=True))
    expect(page.get_by_role("heading", name="Choose an option for your appointment")).to_be_visible()
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_role("link", name="Select an option for your appointment")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_choose_an_option(page: Page) -> None:
    page.goto(url_for("contact_us.choose_an_option", _external=True))
    expect(page.get_by_role("heading", name="Choose an option for your appointment")).to_be_visible()
    page.get_by_text("I will call Civil Legal Advice").click()
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_role("heading", name="Choose an option for your appointment")).not_to_be_visible()
