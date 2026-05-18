from unittest.mock import Mock, patch
from flask import session
from app.categories.constants import FAMILY
from app.means_test import EligibilityState
from app.means_test.api import _check_cfe_eligibility

CAPITAL_THRESHOLD = 800000  # £8000
GROSS_INCOME_THRESHOLD = 265700  # £2657 per month
DISPOSABLE_INCOME_THRESHOLD = 73300  # £733 per month


@patch("app.means_test.api.EligibilityChecker")
class TestCFEMeansTestThresholds:
    def test_capital_threshold(self, mock_checker_class, app, client):
        """Tests that having over £8000 in capital causes the means test to return ineligible."""
        mock_form = Mock()
        mock_form.forms = {
            "about-you": {"has_savings": True},
            "savings": {"investments": 0, "savings": CAPITAL_THRESHOLD, "valuables": 0},
            "income": {},
            "property": {},
        }
        session["eligibility"] = mock_form
        session.category = FAMILY

        # Configure the mock instance to return ELIGIBLE
        mock_instance = mock_checker_class.return_value
        mock_instance.is_eligible_with_reasons.return_value = (EligibilityState.YES, True, True, True)

        result = _check_cfe_eligibility()
        assert result == EligibilityState.YES

        # Configure the mock instance to return INELIGIBLE due to capital
        mock_form.forms["savings"]["savings"] = CAPITAL_THRESHOLD + 1
        session["eligibility"] = mock_form
        mock_instance.is_eligible_with_reasons.return_value = (EligibilityState.NO, True, True, False)

        result = _check_cfe_eligibility()
        assert result == EligibilityState.NO

    def test_gross_income_threshold(self, mock_checker_class, app, client):
        """Tests that having over £2657 in gross income causes the means test to return ineligible."""
        mock_form = Mock()
        mock_form.forms = {
            "about-you": {"is_employed": True},
            "savings": {},
            "income": {
                "earnings": {"interval_period": "per_month", "per_interval_value": GROSS_INCOME_THRESHOLD},
            },
            "property": {},
        }
        session["eligibility"] = mock_form
        session.category = FAMILY

        # Configure the mock instance to return UNKNOWN
        mock_instance = mock_checker_class.return_value
        mock_instance.is_eligible_with_reasons.return_value = (EligibilityState.UNKNOWN, True, True, True)

        result = _check_cfe_eligibility()
        assert result == EligibilityState.UNKNOWN

        # Configure the mock instance to return INELIGIBLE due to gross income
        mock_form.forms["income"]["earnings"] = {
            "interval_period": "per_month",
            "per_interval_value": GROSS_INCOME_THRESHOLD + 1,
        }
        session["eligibility"] = mock_form
        mock_instance.is_eligible_with_reasons.return_value = (EligibilityState.NO, False, True, True)

        result = _check_cfe_eligibility()
        assert result == EligibilityState.NO

    def test_disposable_income_threshold(self, mock_checker_class, app, client):
        """Tests that having over £733 in disposable income causes the means test to return ineligible."""
        mock_form = Mock()
        mock_form.forms = {
            "about-you": {"is_employed": True},
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
        session["eligibility"] = mock_form
        session.category = FAMILY

        # Configure the mock instance to return ELIGIBLE
        mock_instance = mock_checker_class.return_value
        mock_instance.is_eligible_with_reasons.return_value = (EligibilityState.YES, True, True, True)

        result = _check_cfe_eligibility()
        assert result == EligibilityState.YES

        # Configure the mock instance to return INELIGIBLE due to disposable income
        mock_form.forms["income"]["maintenance_received"] = {
            "interval_period": "per_month",
            "per_interval_value": DISPOSABLE_INCOME_THRESHOLD + 1,
        }
        session["eligibility"] = mock_form
        mock_instance.is_eligible_with_reasons.return_value = (EligibilityState.NO, True, False, True)

        result = _check_cfe_eligibility()
        assert result == EligibilityState.NO
