from playwright.sync_api import Page
import pytest


@pytest.mark.usefixtures("live_server")
def test_discrimination(page: Page):
    page.get_by_role("link", name="Discrimination").click()
    page.get_by_label("Work").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_label("Disability").check()
    page.get_by_role("button", name="Continue").click()
