import pytest
from app import Config
from app import create_app
from flask import url_for
import re
from playwright.sync_api import Page
from axe_core_python.sync_playwright import Axe
import json
import os

class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SERVER_NAME = "localhost"
    RATELIMIT_ENABLED = False
    SECRET_KEY = "TEST_KEY"
    ACCESSIBILITY_STANDARDS = ["wcag2a", "wcag2aa"]

@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope="function", autouse=True)
def startup(app, page):
    page.goto(url_for('main.index', _external=True))

@pytest.fixture(scope="function", autouse=True)
def test_accessibility(page: Page):
    directory = "tests/functional_tests/accessibility_output"
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    axe = Axe()
    results = axe.run(page)

    yield axe

    wcag_violations = []

    for violation in results['violations']:
        if set(violation["tags"]) & set(TestConfig.ACCESSIBILITY_STANDARDS):
            wcag_violations.append(violation)
    
    if len(wcag_violations) == 0:
        assert "No WCAG accessibility issues found"
    else:
        # Cleans the URL to remove any invalid characters and replace with _
        invalid_filename_chars = r'[\/:*?"<>|]'
        sanitized_title = re.sub(invalid_filename_chars, '_', page.title())

        max_title_len = 30
        file_path = f"tests/functional_tests/accessibility_output/axe_results_{sanitized_title[:max_title_len]}.json"
        with open(file_path, "w") as file:
            json.dump(wcag_violations, file, indent=4)
        assert not wcag_violations, f"WCAG accessibility issues found: {wcag_violations}"