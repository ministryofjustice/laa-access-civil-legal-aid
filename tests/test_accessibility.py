from playwright.sync_api import Page
from tests.common_steps.accessibility import test_accessibility
import pytest

@pytest.mark.usefixtures("live_server")
def test_base_accessibility(page: Page, test_accessibility):
    pass