
import re
from playwright.sync_api import Page, expect
from axe_core_python.sync_playwright import Axe
import json


def test_accessibility(page: Page):
    axe = Axe()
    results = axe.run(page)
    path = f"playwright/axe/{page.url}_axe_results.json"
    with open(path, "w") as file:
        json.dump(results, file, indent=4)

