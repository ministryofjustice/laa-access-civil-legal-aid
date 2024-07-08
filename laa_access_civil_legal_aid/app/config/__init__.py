import os
from dotenv import load_dotenv

# Allows .env to be used in project for local development.
load_dotenv()


class Config(object):
    CONTACT_EMAIL = os.environ["CONTACT_EMAIL"]
    CONTACT_PHONE = os.environ["CONTACT_PHONE"]
    DEPARTMENT_NAME = os.environ["DEPARTMENT_NAME"]
    DEPARTMENT_URL = os.environ["DEPARTMENT_URL"]
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_STORAGE_URI = os.environ.get("REDIS_URL")
    SECRET_KEY = os.environ["SECRET_KEY"]
    SERVICE_NAME = os.environ["SERVICE_NAME"]
    SERVICE_PHASE = os.environ["SERVICE_PHASE"]
    SERVICE_URL = os.environ["SERVICE_URL"]
    SESSION_COOKIE_HTTPONLY = True
    # SESSION_COOKIE_SECURE = True
