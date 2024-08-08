
import re
from playwright.sync_api import Page
from axe_core_python.sync_playwright import Axe
import json
import pytest

@pytest.fixture()
def test_accessibility(page: Page):
    axe = Axe()
    results = axe.run(page)
    file_path = f"playwright/axe/{page.title()}_axe_results.json"
    with open(file_path, "w") as file:
        json.dump(results.get('violations'), file, indent=4)
    
    assert not results.get('violations'), f"Accessibility issues found: {results.get('violations')}"

