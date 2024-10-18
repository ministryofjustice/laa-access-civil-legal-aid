from playwright.sync_api import Page, expect
import pytest


@pytest.mark.usefixtures("live_server")
def test_clinical_negligence(page: Page):
    page.get_by_role("button", name="More problems covered by").click()
    page.get_by_role("link", name="Clinical negligence in babies").click()
    expect(page.get_by_role("heading", name="Find a legal adviser")).to_be_visible()
    expect(page.get_by_text("For clinical negligence")).to_be_visible()
