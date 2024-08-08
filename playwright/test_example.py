import re
from playwright.sync_api import Page, expect
from accessibility import test_accessibility

def test_home_page_accessibility(page: Page):
    page.goto("https://playwright.dev/")
    expect(page).to_have_title(re.compile("Playwright"))
    test_accessibility(page)