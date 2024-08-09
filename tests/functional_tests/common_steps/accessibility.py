
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

    directory = "tests/functional_tests/accessibility_output"
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    axe = Axe()
    results = axe.run(page)

    wcag_violations = [violation for violation in results['violations'] if any(tag in violation['tags'] for tag in ["wcag2a", "wcag2aa"])]
    
    if len(wcag_violations) == 0:
        assert f"No WCAG accessibility issues found"
    else:
        sanitized_title = re.sub(r'[\/:*?"<>|]', '_', page.title())
        file_path = f"tests/functional_tests/accessibility_output/axe_results_{sanitized_title[:30]}.json"
        with open(file_path, "w") as file:
            json.dump(wcag_violations, file, indent=4)
        assert not wcag_violations, f"WCAG accessibility issues found: {wcag_violations}"

