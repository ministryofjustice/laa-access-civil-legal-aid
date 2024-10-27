from playwright.sync_api import Page
import pytest


@pytest.mark.usefixtures("live_server")
def test_clinical_negligence(page: Page):
    page.get_by_role("button", name="More problems covered by").click()
    page.get_by_role("link", name="Clinical negligence in babies").click()
