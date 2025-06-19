import pytest
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
def test_service_url(page: Page):
    expect(
        page.get_by_role("link", name="Check if you can get legal aid")
    ).to_have_attribute("href", value="/")


@pytest.mark.usefixtures("live_server")
def test_gov_uk_url(page: Page):
    expect(page.get_by_role("link", name="GOV.UK")).to_have_attribute(
        "href", "https://www.gov.uk"
    )
