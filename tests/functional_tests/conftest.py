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
# Also logs to RACE_SPIKE_LOG so we can see the child process's own
# stdout/stderr (werkzeug bind errors, tracebacks) which pytest's per-test
# capture would otherwise swallow since live_server is session-scoped.
# Remove once LGA-3883 is confirmed/fixed.
if os.environ.get("FORCE_LIVE_SERVER_RACE"):
    import pytest_flask.live_server as _live_server_mod

    _race_log_path = os.environ.get("RACE_SPIKE_LOG", "/tmp/race_spike.log")

    def _race_log(msg):
        worker = os.environ.get("PYTEST_XDIST_WORKER", "main")
        with open(_race_log_path, "a") as f:
            f.write(f"{time.time():.3f} [{worker}] {msg}\n")

    def _instrumented_start(self):
        _race_log(f"pid={os.getpid()} about to sleep before starting live_server on port={self.port}")
        time.sleep(float(os.environ.get("FORCE_LIVE_SERVER_RACE_DELAY", "2")))
        _race_log(f"pid={os.getpid()} slept, now forking child for port={self.port}")

        def worker(app, host, port):
            import sys
            import traceback

            log_file = open(_race_log_path, "a", buffering=1)
            sys.stdout = log_file
            sys.stderr = log_file
            worker_name = os.environ.get("PYTEST_XDIST_WORKER", "main")
            try:
                log_file.write(f"{time.time():.3f} [{worker_name}] child pid={os.getpid()} binding {host}:{port}\n")
                app.run(host=host, port=port, use_reloader=False, threaded=True)
            except BaseException:
                log_file.write(
                    f"{time.time():.3f} [{worker_name}] child pid={os.getpid()} CRASHED binding/running on port={port}\n"
                )
                traceback.print_exc(file=log_file)
                raise

        self._process = _live_server_mod.multiprocessing.Process(target=worker, args=(self.app, self.host, self.port))
        self._process.daemon = True
        self._process.start()
        _race_log(f"pid={os.getpid()} forked child pid={self._process.pid} for port={self.port}")

        keep_trying = True
        start_time = time.time()
        while keep_trying:
            elapsed_time = time.time() - start_time
            if elapsed_time > self.wait:
                _race_log(
                    f"pid={os.getpid()} TIMED OUT waiting for port={self.port} after {self.wait}s, "
                    f"child alive={self._process.is_alive()}"
                )
                pytest.fail(f"Failed to start the server after {self.wait} seconds.")
            if self._is_ready():
                keep_trying = False
        _race_log(f"pid={os.getpid()} live_server READY on port={self.port} after {time.time() - start_time:.2f}s")

    _live_server_mod.LiveServer.start = _instrumented_start

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
def startup(app, page, request):
    try:
        page.goto(url_for("categories.index", _external=True))
    except Exception:
        if os.environ.get("FORCE_LIVE_SERVER_RACE"):
            live_server = request.getfixturevalue("live_server")
            alive = live_server._process.is_alive() if live_server._process else None
            _race_log(
                f"pid={os.getpid()} startup FAILED for {request.node.nodeid}, "
                f"live_server port={live_server.port} child_pid={live_server._process.pid if live_server._process else None} "
                f"child_alive={alive}"
            )
        raise
