from playwright.sync_api import Page, expect
import pytest


@pytest.mark.usefixtures("live_server")
def test_discrimination(page: Page):
    page.get_by_role("link", name="Discrimination").click()
    page.get_by_label("Work").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_label("Disability").check()
    page.get_by_role("button", name="Continue").click()
    expect(
        page.get_by_role("link", name="Check if you can get legal aid")
    ).to_be_visible()
    expect(
        page.get_by_role("heading", name="Legal aid is available for")
    ).to_be_visible()
