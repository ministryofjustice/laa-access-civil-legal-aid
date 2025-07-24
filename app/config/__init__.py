import os
from dotenv import load_dotenv
from datetime import timedelta
from .enums import MeansTestCalculator

# Allows .env to be used in project for local development.
load_dotenv()


class Config(object):
    ENVIRONMENT = os.environ.get("CLA_ENVIRONMENT", "production")
    GOV_UK_START_PAGE = os.environ.get("GOV_UK_START_PAGE", "https://www.gov.uk/check-legal-aid")
    WELSH_GOV_UK_START_PAGE = os.environ.get(
        "WELSH_GOV_UK_START_PAGE",
        "https://www.gov.uk/gwirio-os-ydych-yn-gymwys-i-gael-cymorth-cyfreithiol",
    )
    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "")
    CONTACT_PHONE = os.environ.get("CONTACT_PHONE", "")
    DEPARTMENT_NAME = os.environ.get("DEPARTMENT_NAME", "MOJ Digital")
    DEPARTMENT_URL = os.environ.get("DEPARTMENT_URL", "https://mojdigital.blog.gov.uk/")
    TESTING = False
    RATELIMIT_ENABLED = os.environ.get("RATELIMIT_ENABLED", "True").lower() == "true"
    RATELIMIT_HEADERS_ENABLED = RATELIMIT_ENABLED
    RATELIMIT_STORAGE_URI = os.environ.get("REDIS_URL")
    SECRET_KEY = os.environ["SECRET_KEY"]
    SERVICE_NAME = "Check if you can get legal aid"
    SERVICE_PHASE = os.environ.get("SERVICE_PHASE", "Beta")
    SERVICE_URL = os.environ.get("SERVICE_URL", "")
    SESSION_COOKIE_HTTP_ONLY = ENVIRONMENT != "local"
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    LANGUAGES = {"en": "English", "cy": "Welsh"}
    SERVICE_UNAVAILABLE = os.environ.get("MAINTENANCE_MODE", "False").lower() == "true"
    FALA_URL = os.environ.get("FALA_URL", "https://find-legal-advice.justice.gov.uk")
    CLA_BACKEND_URL = os.environ.get("CLA_BACKEND_URL", "http://localhost:8010")
    SESSION_TIMEOUT = timedelta(minutes=30)
    SESSION_COOKIE_SECURE = True
    OS_PLACES_API_KEY = os.environ.get("OS_PLACES_API_KEY")
    EMAIL_ORCHESTRATOR_URL = os.environ.get("EMAIL_ORCHESTRATOR_URL")
    CFE_URL = os.environ.get("CFE_URL", "https://cfe-civil.cloud-platform.service.justice.gov.uk")
    MEANS_TEST_CALCULATOR: MeansTestCalculator = MeansTestCalculator.from_env(
        os.getenv("MEANS_TEST_CALCULATOR"), default=MeansTestCalculator.CLA_BACKEND
    )
    RUN_MEANS_TEST_CALCULATORS_IN_PARALLEL = (
        os.environ.get("RUN_MEANS_TEST_CALCULATORS_IN_PARALLEL", "True").lower() == "true"
    )
