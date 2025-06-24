import pytest
from flask import url_for
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
def test_contact_us_journey(page: Page):
    """Test the reverse flow through a contact us journey"""
    page.get_by_role("link", name="Children, families,").click()
    page.get_by_role("link", name="Children and social services").click()
    expect(
        page.get_by_role("heading", name="Contact Civil Legal Advice")
    ).to_be_visible()
    page.get_by_role("button", name="Back").click()
    expect(
        page.get_by_role("heading", name="Children, families, relationships")
    ).to_be_visible()
    page.get_by_role("button", name="Back").click()
    expect(
        page.get_by_role("heading", name="Find problems covered by legal aid")
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_in_scope_journey(page: Page):
    """Test the reverse flow through an in-scope journey"""
    page.get_by_role("link", name="Housing, homelessness, losing").click()
    page.get_by_role("link", name="Homelessness").click()
    page.get_by_role("button", name="Check if you qualify").click()
    expect(page.get_by_role("heading", name="About you")).to_be_visible()
    page.get_by_role("button", name="Back").click()
    expect(
        page.get_by_role("heading", name="Legal aid is available for")
    ).to_be_visible()
    page.get_by_role("button", name="Back").click()
    expect(
        page.get_by_role("heading", name="Housing, homelessness, losing")
    ).to_be_visible()
    page.get_by_role("button", name="Back").click()
    expect(page.get_by_role("heading", name="Find problems covered by")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_out_of_scope_journey(page: Page):
    """Test the reverse flow through an out-of-scope journey"""
    page.get_by_role("link", name="Benefits").click()
    page.get_by_role("radio", name="None of these").check()
    page.get_by_role("button", name="Continue").click()
    expect(
        page.get_by_role("heading", name="Sorry, you’re not likely to get legal aid")
    ).to_be_visible()
    page.get_by_role("button", name="Back").click()
    expect(
        page.get_by_role("heading", name="Appeal a decision about your")
    ).to_be_visible()
    page.get_by_role("button", name="Back").click()
    expect(page.get_by_role("heading", name="Find problems covered by")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_fala_journey(page: Page):
    """Test the reverse flow through a FALA journey"""
    page.get_by_role("link", name="Asylum and immigration").click()
    page.get_by_role("link", name="Applying for asylum").click()
    page.get_by_role("textbox", name="Postcode").fill("SW1A")
    page.get_by_role("button", name="Search").click()
    expect(page.get_by_role("heading", name="Contact a legal adviser")).to_be_visible()
    page.get_by_role("button", name="Back").click()
    expect(page.get_by_role("heading", name="Find a legal adviser")).to_be_visible()
    page.get_by_role("button", name="Back").click()
    expect(page.get_by_role("heading", name="Asylum and immigration")).to_be_visible()
    page.get_by_role("button", name="Back").click()
    expect(page.get_by_role("heading", name="Find problems covered by")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_fallback(page: Page):
    """Test that we go to session expired page if we press back when referred from an external page"""
    page.goto("https://www.gov.uk")
    page.goto(url_for("means_test.about-you", _external=True))
    page.get_by_role("button", name="Back").click()
    expect(
        page.get_by_role("heading", name="You’ve reached the end of this service")
    ).to_be_visible()
