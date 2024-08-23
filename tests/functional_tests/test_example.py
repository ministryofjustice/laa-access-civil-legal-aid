from playwright.sync_api import Page
import pytest


@pytest.mark.usefixtures("live_server")
def test_base_accessibility(page: Page):
    pass
