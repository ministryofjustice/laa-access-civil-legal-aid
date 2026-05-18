import pytest
from app import create_app, Config


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    RATELIMIT_ENABLED = False
    SECRET_KEY = "TEST_KEY"
    CFE_URL = "http://cfe-civil.cfe-civil-staging.svc.cluster.local"


@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)
    return app


@pytest.fixture()
def client(app):
    return app.test_client()
