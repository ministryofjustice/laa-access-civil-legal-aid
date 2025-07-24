from unittest.mock import Mock
from flask import session
from app.categories.constants import FAMILY
from app.means_test import EligibilityState
from app.means_test.api import _check_cfe_eligibility

CAPITAL_THRESHOLD = 800000  # £8000
GROSS_INCOME_THRESHOLD = 265700  # £2657 per month
DISPOSABLE_INCOME_THRESHOLD = 73300  # £733 per month


class TestCFEMeansTestThresholds:
    def test_capital_threshold(self, app, client):
        """Tests that having over £8000 in capital causes the means test to return ineligible."""
        mock = Mock()
        mock.forms = {
            "about-you": {
                "has_savings": True,
            },
            "savings": {"investments": 0, "savings": CAPITAL_THRESHOLD, "valuables": 0},
            "income": {},
            "property": {},
        }

        session["eligibility"] = mock
        session.category = FAMILY

        result = _check_cfe_eligibility()
        assert result == EligibilityState.YES

        mock.forms["savings"]["savings"] = CAPITAL_THRESHOLD + 1
        session["eligibility"] = mock
        result = _check_cfe_eligibility()
        assert result == EligibilityState.NO

    def test_gross_income_threshold(self, app, client):
        """Tests that having over £2657 in gross income causes the means test to return ineligible."""
        mock = Mock()
        mock.forms = {
            "about-you": {
                "is_employed": True,
            },
            "savings": {},
            "income": {
                "earnings": {"interval_period": "per_month", "per_interval_value": GROSS_INCOME_THRESHOLD},
            },
            "property": {},
        }

        session["eligibility"] = mock
        session.category = FAMILY

        result = _check_cfe_eligibility()
        assert (
            result == EligibilityState.UNKNOWN
        )  # Unknown as deductions could reduce the client's disposable income to below the threshold

        mock.forms["income"]["earnings"] = {
            "interval_period": "per_month",
            "per_interval_value": GROSS_INCOME_THRESHOLD + 1,
        }
        session["eligibility"] = mock
        result = _check_cfe_eligibility()
        assert result == EligibilityState.NO

    def test_disposable_income_threshold(self, app, client):
        """Tests that having over £733 in disposable income causes the means test to return ineligible."""
        mock = Mock()
        mock.forms = {
            "about-you": {
                "is_employed": True,
            },
            "savings": {"investments": 0, "savings": 0, "valuables": 0},
            "income": {
                "maintenance_received": {
                    "interval_period": "per_month",
                    "per_interval_value": DISPOSABLE_INCOME_THRESHOLD,
                },
            },
            "outgoings": {},
            "property": {},
        }

        session["eligibility"] = mock
        session.category = FAMILY

        result = _check_cfe_eligibility()
        assert result == EligibilityState.YES

        mock.forms["income"]["maintenance_received"] = {
            "interval_period": "per_month",
            "per_interval_value": DISPOSABLE_INCOME_THRESHOLD + 1,
        }
        session["eligibility"] = mock
        result = _check_cfe_eligibility()
        assert result == EligibilityState.NO
