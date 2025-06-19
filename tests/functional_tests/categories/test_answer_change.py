from flask import url_for
from playwright.sync_api import Page, expect
import pytest


@pytest.mark.usefixtures("live_server")
def test_change_domestic_abuse(page: Page):
    page.get_by_role("link", name="Domestic abuse").click()
    page.get_by_role(
        "link", name="Help to keep yourself safe and protect children"
    ).click()

    page.get_by_role("radio", name="No").click()
    page.get_by_role("button", name="Continue").click()

    page.get_by_role("button", name="Back").click()
    page.get_by_role("button", name="Back").click()

    page.get_by_role("link", name="Leaving an abusive relationship").click()
    expect(page.get_by_role("radio", name="No")).not_to_be_checked()


def test_change_send(page: Page):
    page.get_by_role(
        "link", name="Special educational needs and disability (SEND)"
    ).click()
    page.get_by_role("link", name="Help with a child or young person's SEND").click()

    page.get_by_role("radio", name="No").click()
    page.get_by_role("button", name="Continue").click()

    page.get_by_role("button", name="Back").click()
    page.get_by_role("button", name="Back").click()

    page.get_by_role("link", name="SEND tribunals").click()
    expect(page.get_by_role("radio", name="No")).not_to_be_checked()


@pytest.mark.usefixtures("live_server")
def test_bug_lga_3746_multiple_subcategories(page: Page):
    url = url_for("main.start", _external=True)
    assert url.endswith("/start"), url
    page.goto(url)
    expect(
        page.get_by_role("heading", name="Find problems covered by legal aid")
    ).to_be_visible()

    page.get_by_role("link", name="Domestic abuse").click()
    page.get_by_role(
        "link", name="Problems with neighbours, landlords or other people"
    ).click()
    expect(
        page.get_by_role("heading", name="Contact Civil Legal Advice")
    ).to_be_visible()

    # Change category
    url = url_for("categories.housing.landing", _external=True)
    page.goto(url)
    page.get_by_role("link", name="Homelessness").click()
    expect(
        page.get_by_role(
            "heading", name="Legal aid is available for this type of problem"
        )
    ).to_be_visible()
