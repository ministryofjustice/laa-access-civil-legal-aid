import pytest
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
def test_benefits_referral(page: Page):
    page.get_by_role("link", name="Benefits").click()
    page.get_by_role("radio", name="None of the above").check()
    page.get_by_role("button", name="Continue").click()
    expect(
        page.get_by_role("heading", name="Legal aid doesn’t cover all problems")
    ).to_be_visible()
    expect(
        page.get_by_role("heading", name="Help organisations for welfare benefits")
    ).to_be_visible()
    page.get_by_role("button", name="Find a solicitor").click()
    expect(page.get_by_role("heading", name="Find a legal adviser")).to_be_visible()
    expect(page.get_by_text("For welfare benefits")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_domestic_abuse_referral(page: Page):
    page.get_by_role("link", name="Domestic abuse").click()
    page.get_by_role("link", name="Next steps to get help").check()
    expect(
        page.get_by_role("heading", name="Legal aid doesn’t cover all problems")
    ).to_be_visible()
    page.get_by_role("button", name="Find a solicitor").click()
    expect(page.get_by_role("heading", name="Find a legal adviser")).to_be_visible()
    expect(page.get_by_text("For family")).to_be_visible()
