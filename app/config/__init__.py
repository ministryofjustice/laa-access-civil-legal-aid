import os
from dotenv import load_dotenv

# Allows .env to be used in project for local development.
load_dotenv()


class Config(object):
    ENVIRONMENT = os.environ.get("CLA_ENVIRONMENT", "production")
    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "")
    CONTACT_PHONE = os.environ.get("CONTACT_PHONE", "")
    DEPARTMENT_NAME = os.environ.get("DEPARTMENT_NAME", "MOJ Digital")
    DEPARTMENT_URL = os.environ.get("DEPARTMENT_URL", "https://mojdigital.blog.gov.uk/")
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_STORAGE_URI = os.environ.get("REDIS_URL")
    SECRET_KEY = os.environ["SECRET_KEY"]
    SERVICE_NAME = os.environ.get("SERVICE_NAME", "Access Civil Legal Aid")
    SERVICE_PHASE = os.environ.get("SERVICE_PHASE", "Beta")
    SERVICE_URL = os.environ.get("SERVICE_URL", "")
    SESSION_COOKIE_HTTPONLY = True
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    LANGUAGES = {"en": "English", "cy": "Welsh"}
    SERVICE_UNAVAILABLE = os.environ.get("MAINTENANCE_MODE", "False").lower() == "true"
    CLA_PUBLIC_URL = os.environ.get(
        "CLA_PUBLIC_URL", "https://staging.checklegalaid.service.gov.uk"
    )
