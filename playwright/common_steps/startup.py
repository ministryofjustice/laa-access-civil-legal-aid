import re
from playwright.sync_api import Page, expect
from common_steps.accessibility import test_accessibility
import pytest

@pytest.fixture(autouse=True)
def open_base_url(page: Page):
    page.goto("http://127.0.0.1:8020/")