import pytest
from app import Config
from app import create_app
from unittest.mock import patch
from app.api import BackendAPIClient


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SERVER_NAME = "localhost"
    RATELIMIT_ENABLED = False
    SECRET_KEY = "TEST_KEY"
    CLA_BACKEND_URL = "http://backend-test.local"
    WTF_CSRF_ENABLED = False


@pytest.fixture(scope="session", autouse=True)
def mock_cache():
    with patch("app.extensions.cache") as mock:
        mock.memoize = lambda *args, **kwargs: lambda f: f
        yield mock


@pytest.fixture(scope="session")
def app():
    return create_app(TestConfig)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def api_client(app):
    with app.app_context():
        return BackendAPIClient()
