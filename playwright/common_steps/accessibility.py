
import re
from playwright.sync_api import Page
from axe_core_python.sync_playwright import Axe
import json
import pytest
import os

@pytest.fixture()
def test_accessibility(page: Page):
    # Ensures run after test
    yield
    
    directory = "playwright/axe"
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    axe = Axe()
    results = axe.run(page)
    sanitized_title = re.sub(r'[\/:*?"<>|]', '_', page.title())
    file_path = f"playwright/axe/{sanitized_title}_axe_results.json"
    with open(file_path, "w+") as file:
        json.dump(results.get('violations'), file, indent=4)

