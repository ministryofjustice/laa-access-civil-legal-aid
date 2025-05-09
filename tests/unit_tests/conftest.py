import pytest
from app import Config, SessionInterface
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
    FALA_URL = "https://staging.find-legal-advice.justice.gov.uk"
    WTF_CSRF_ENABLED = False


@pytest.fixture(scope="session", autouse=True)
def mock_cache():
    with patch("app.extensions.cache") as mock:
        mock.memoize = lambda *args, **kwargs: lambda f: f
        yield mock


@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)
    app.session_interface = SessionInterface()
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def api_client(app):
    with app.app_context():
        return BackendAPIClient()


@pytest.fixture
def mock_url_for():
    with patch("app.categories.views.url_for") as mock:

        def side_effect(*args, **kwargs):
            if kwargs and "endpoint" in kwargs:
                return f"/mocked/{kwargs['endpoint']}"
            return f"/mocked/{args[0]}"

        mock.side_effect = side_effect
        yield mock
