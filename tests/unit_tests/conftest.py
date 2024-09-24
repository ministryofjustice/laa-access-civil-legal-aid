import pytest
from app import Config
from app import create_app


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SERVER_NAME = "localhost"
    RATELIMIT_ENABLED = False
    SECRET_KEY = "TEST_KEY"


@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
