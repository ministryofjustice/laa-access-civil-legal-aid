import pytest
from app import Config
from app import create_app
from flask import url_for


import multiprocessing

try:
    # From python 3.14 the default fork method has change from fork to forkserver https://docs.python.org/3/whatsnew/3.14.html#concurrent-futures
    # Without this there will we will get pickle errors when running the functional tests https://github.com/ministryofjustice/laa-access-civil-legal-aid/actions/runs/24890132119/job/72879999685
    # This needs to be fixed in the pytest-flask package
    #
    # Brief explanation of forkserver
    # forkserver (now the defaults/preferred methods in 3.14) start a fresh process and use pickle to send data over.
    # Since Python's pickle cannot handle local functions (nested functions inside another function),
    # it throws the PicklingError
    multiprocessing.set_start_method("fork", force=True)
except RuntimeError:
    pass


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
    }


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SERVER_NAME = "localhost"
    RATELIMIT_ENABLED = False
    SECRET_KEY = "TEST_KEY"


@pytest.fixture(scope="session")
def app(config=TestConfig):
    return create_app(config)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope="function", autouse=True)
def startup(app, page):
    page.goto(url_for("categories.index", _external=True))
