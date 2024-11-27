import pytest
from playwright.sync_api import Page


@pytest.mark.usefixtures("live_server")
def test_locale(live_server, page: Page):
    assert page.locator("html").get_attribute("lang") == "en"
    link = page.locator("a[x-data='language-switcher']")
    assert link.text_content().strip() == "Cymraeg"
    assert link.get_attribute("href") == "/locale/cy"

    link.click()

    assert page.locator("html").get_attribute("lang") == "cy"
    link = page.locator("a[x-data='language-switcher']")
    assert link.text_content().strip() == "English"
    assert link.get_attribute("href") == "/locale/en"
