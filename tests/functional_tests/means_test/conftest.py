from playwright.sync_api import Page
import pytest


@pytest.fixture
def navigate_to_means_test(page: Page):
    page.get_by_role("link", name="Housing, homelessness, losing your home").click()
    page.get_by_role("link", name="Homelessness").click()
    page.get_by_role("button", name="Check if you qualify financially").click()
    return page
