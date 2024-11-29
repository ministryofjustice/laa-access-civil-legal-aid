from playwright.sync_api import Page, expect
import pytest


@pytest.mark.usefixtures("live_server")
def test_housing(page: Page):
    page.get_by_role("link", name="Housing, homelessness, losing your home").click()
    page.get_by_role("link", name="Homelessness").click()
    expect(
        page.get_by_text("Legal aid is available for this type of problem")
    ).to_be_visible()
