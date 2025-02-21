import pytest
from flask import url_for
import re
from playwright.sync_api import Page
from axe_core_python.sync_playwright import Axe
import json
import os
import shutil


ACCESSIBILITY_STANDARDS = ["wcag2a", "wcag2aa"]


def check_accessibility(page: Page):
    """
    Inserts axe core python into a page at the yield step
    to run accessibility based testing. Axe will run on
    the page defined in the function.
    """
    if page.title() != "localhost":
        directory = "tests/functional_tests/accessibility_output"
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        axe = Axe()

        """ We disable the aria-allowed-attr as GOV.UK Frontend uses aria-expanded on radio buttons, which is not allowed.
        The GOV.UK Frontend team say: "No negative effects to having the attribute present have been found. 
        Allowing `aria-expanded` on radios is an open proposal:"
        """
        options = '{"rules": {"aria-allowed-attr": {"enabled": false}}}'  # This is a string as this is passed directly to the javascript axe.run function

        results = axe.run(page, options=options)

        wcag_violations = []

        for violation in results["violations"]:
            if set(violation["tags"]) & set(ACCESSIBILITY_STANDARDS):
                wcag_violations.append(violation)

        if len(wcag_violations) == 0:
            assert "No WCAG accessibility issues found"
        else:
            # Cleans the URL to remove any invalid characters and replace with _
            invalid_filename_chars = r'[\/:*?"<>|]'
            sanitized_title = re.sub(invalid_filename_chars, "_", page.title())

            max_title_len = 30
            file_name = f"axe_results_{sanitized_title[:max_title_len]}.json"
            file_path = os.path.join(directory, file_name)
            with open(file_path, "w") as file:
                json.dump(wcag_violations, file, indent=4)


@pytest.mark.usefixtures("live_server")
def test_all_page_accessibility(app, page: Page):
    ignored_routes = [
        "static",
        "/",
        "main.status",
        "main.set_locale",
        "contact.geocode",
    ]
    shutil.rmtree("tests/functional_tests/accessibility_output", ignore_errors=True)
    routes = app.view_functions
    for route in routes:
        if route not in ignored_routes:
            full_url = url_for(route, _external=True)
            page.goto(full_url)
            check_accessibility(page)


def test_accessibility_folder():
    path = "tests/functional_tests/accessibility_output"
    if not any(os.scandir(path)):
        assert True
    else:
        assert not "WCAG accessibility issues found"
