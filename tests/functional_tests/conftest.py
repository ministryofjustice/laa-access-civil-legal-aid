import os
import time

import pytest
from app import Config
from app import create_app
from flask import url_for


import multiprocessing

# LGA-3883 spike: force the pytest-flask live_server port TOCTOU race
# (fixtures.py binds port 0, closes the probe socket, then forks a child
# that rebinds the same port number later). Widening the gap here makes
# an OS port reuse collision far more likely to land inside the window,
# so it can be caught reliably in CI instead of ~never locally.
# Remove once LGA-3883 is confirmed/fixed.
if os.environ.get("FORCE_LIVE_SERVER_RACE"):
    import pytest_flask.live_server as _live_server_mod

    _orig_start = _live_server_mod.LiveServer.start

    def _slow_start(self):
        print(f"[race-spike] sleeping before binding port {self.port}", flush=True)
        time.sleep(float(os.environ.get("FORCE_LIVE_SERVER_RACE_DELAY", "2")))
        return _orig_start(self)

    _live_server_mod.LiveServer.start = _slow_start

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
