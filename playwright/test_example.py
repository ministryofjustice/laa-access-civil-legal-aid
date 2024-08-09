import re
from playwright.sync_api import Page, expect
from common_steps.startup import open_base_url
from common_steps.accessibility import test_accessibility


def test_has_title(page: Page, test_accessibility):
    page.goto('https://mojdigital.blog.gov.uk/')