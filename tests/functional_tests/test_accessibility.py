import pytest
from flask import url_for
import re
from playwright.sync_api import Page
from axe_core_python.sync_playwright import Axe
import json
import os
import shutil
from app.categories.traversal import category_traversal, NavigationResult


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
        results = axe.run(page)

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
def test_question_page_accessibility(app, page: Page):
    """As the question page URLs depend on the question routes we need get all valid category paths and test each page"""

    def get_all_question_pages(category_traversal_map) -> dict[str, NavigationResult]:
        """Generate dictionary of path components for all question pages
        Only includes paths that end on a question page."""
        all_paths = category_traversal_map.get_all_valid_paths()

        full_paths = {}

        for path in all_paths:
            result = category_traversal_map.route_cache[path]
            if result.is_redirect:
                continue
            full_paths[path] = result
        return full_paths

    all_question_pages_paths = get_all_question_pages(category_traversal)
    for path in all_question_pages_paths:
        full_url = url_for("categories.question_page", path=path, _external=True)
        page.goto(full_url)
        check_accessibility(page)


@pytest.mark.usefixtures("live_server")
def test_all_page_accessibility(app, page: Page):
    # categories.question_page is ignored as we want to run accessibility testing against each question individually.
    ignored_routes = [
        "static",
        "/",
        "main.status",
        "main.set_locale",
        "categories.question_page",
        "categories.routing_map",
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
