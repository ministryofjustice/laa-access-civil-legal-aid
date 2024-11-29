from playwright.sync_api import Page, expect
import pytest


@pytest.mark.usefixtures("live_server")
def test_domestic_abuse_at_immediate_risk_of_harm(page: Page):
    """If the user is at immediate risk of harm they should be immediately routed to the /contact page."""
    page.get_by_role("link", name="Domestic abuse").click()
    page.get_by_role("link", name="Help to protect you and your").click()
    page.get_by_label("Yes").check()
    page.get_by_role("button", name="Continue").click()
    expect(
        page.get_by_text("Legal aid is available for this type of problem")
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_domestic_abuse_not_at_immediate_risk_of_harm(page: Page):
    """This is where the current prototype journey ends, there are no onward pages yet."""
    page.get_by_role("link", name="Domestic abuse").click()
    page.get_by_role("link", name="Help to protect you and your").click()
    page.get_by_label("No").check()
    page.get_by_role("button", name="Continue").click()
    expect(
        page.get_by_text("Legal aid is available for this type of problem")
    ).to_be_visible()
