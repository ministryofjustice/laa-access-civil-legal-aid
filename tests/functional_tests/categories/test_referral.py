import pytest
from playwright.sync_api import Page, expect

REFERRAL_PAGE_HEADING = "Legal aid doesn’t cover all types of problem"


@pytest.mark.usefixtures("live_server")
def test_benefits_referral(page: Page):
    page.get_by_role("link", name="Benefits").click()
    page.get_by_role("radio", name="None of these").check()
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_role("heading", name=REFERRAL_PAGE_HEADING)).to_be_visible()
    expect(
        page.get_by_role(
            "heading", name="Help organisations for problems about welfare benefits"
        )
    ).to_be_visible()
    page.get_by_role("link", name="ask a legal adviser").click()
    expect(page.get_by_role("heading", name="Find a legal adviser")).to_be_visible()
    expect(page.get_by_text("For welfare benefits")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_domestic_abuse_referral(page: Page):
    page.get_by_role("link", name="Domestic abuse").click()
    page.get_by_role("link", name="Next steps to get help").click()
    expect(page.get_by_role("heading", name=REFERRAL_PAGE_HEADING)).to_be_visible()
    page.get_by_role("link", name="ask a legal adviser").click()
    expect(page.get_by_role("heading", name="Find a legal adviser")).to_be_visible()
    expect(page.get_by_text("For family")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_send_referral(page: Page):
    page.get_by_role("link", name="Special educational needs and disability").click()
    page.get_by_role("link", name="Next steps to get help").click()
    expect(page.get_by_role("heading", name=REFERRAL_PAGE_HEADING)).to_be_visible()
    expect(
        page.get_by_role(
            "heading",
            name="Help organisations for problems about special educational needs and disability (SEND)",
        )
    ).to_be_visible()
    page.get_by_role("link", name="ask a legal adviser").click()
    expect(page.get_by_role("heading", name="Find a legal adviser")).to_be_visible()
    expect(page.get_by_text("For education")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_find_a_solicitor_link(page: Page):
    page.get_by_role("link", name="Special educational needs and disability").click()
    page.get_by_role("link", name="Next steps to get help").click()
    expect(page.get_by_role("heading", name=REFERRAL_PAGE_HEADING)).to_be_visible()

    page.get_by_role("button", name="Find a solicitor").click()
    expect(
        page.get_by_role("heading", name="Find legal advice and information")
    ).to_be_visible()
