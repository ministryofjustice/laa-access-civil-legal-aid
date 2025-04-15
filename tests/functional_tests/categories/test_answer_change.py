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
