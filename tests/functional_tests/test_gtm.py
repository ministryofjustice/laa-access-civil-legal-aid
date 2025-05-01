from playwright.sync_api import Page
import pytest


@pytest.mark.usefixtures("live_server")
def test_gtm_anon_accepted(page: Page):
    page.get_by_role("button", name="accept").click()
    page.get_by_role("link", name="Housing, homelessness, losing your home").click()
    cookies = page.context.cookies()
    gtm_cookie = next((c for c in cookies if c["name"] == "gtm_anon_id"), None)
    assert gtm_cookie is not None
    assert len(gtm_cookie["value"]) == 36
    page.get_by_role("link", name="Homelessness").click()
    cookies = page.context.cookies()
    gtm_cookie_2 = next((c for c in cookies if c["name"] == "gtm_anon_id"), None)

    assert gtm_cookie == gtm_cookie_2


@pytest.mark.usefixtures("live_server")
def test_gtm_anon_not_accepted(page: Page):
    page.get_by_role("button", name="reject").click()
    page.get_by_role("link", name="Housing, homelessness, losing your home").click()
    cookies = page.context.cookies()
    gtm_cookie = next((c for c in cookies if c["name"] == "gtm_anon_id"), None)
    assert gtm_cookie is None
