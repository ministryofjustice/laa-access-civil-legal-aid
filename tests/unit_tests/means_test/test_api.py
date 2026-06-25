from unittest.mock import patch, Mock
from flask import session
from app.means_test import api
from app.means_test.constants import EligibilityState
from app.constants.means_tests import IneligibleReason


class TestCheckEligibility:
    def test_check_eligibility_returns_cfe_result(self, client):
        with (
            patch("app.means_test.api.CFEMeansTestPayload"),
            patch("app.means_test.api.create_update_case_reference"),
            patch("app.means_test.api.CaseData"),
            patch("app.means_test.api.EligibilityChecker") as mock_checker,
        ):
            mock_checker.return_value.is_eligible_with_reasons.return_value = (
                EligibilityState.YES,
                True,
                True,
                True,
            )

            result = api.check_eligibility()

            assert result == EligibilityState.YES

    def test_check_eligibility_syncs_case_reference(self, client):
        with (
            patch("app.means_test.api.CFEMeansTestPayload"),
            patch("app.means_test.api.create_update_case_reference") as mock_sync,
            patch("app.means_test.api.CaseData"),
            patch("app.means_test.api.EligibilityChecker") as mock_checker,
        ):
            mock_checker.return_value.is_eligible_with_reasons.return_value = (
                EligibilityState.YES,
                True,
                True,
                True,
            )

            api.check_eligibility()

            mock_sync.assert_called_once()


class TestIneligibleReasons:
    def _make_checker(self, mock_checker, result, gross_ok, disp_ok, cap_ok):
        mock_checker.return_value.is_eligible_with_reasons.return_value = (result, gross_ok, disp_ok, cap_ok)

    def test_no_reasons_set_when_eligible(self, client):
        with (
            patch("app.means_test.api.CFEMeansTestPayload"),
            patch("app.means_test.api.create_update_case_reference"),
            patch("app.means_test.api.CaseData"),
            patch("app.means_test.api.EligibilityChecker") as mock_checker,
        ):
            self._make_checker(mock_checker, EligibilityState.YES, True, True, True)

            api.check_eligibility()

            assert session.get("ineligible_reasons") is None

    def test_gross_income_reason_set(self, client):
        with (
            patch("app.means_test.api.CFEMeansTestPayload"),
            patch("app.means_test.api.create_update_case_reference"),
            patch("app.means_test.api.CaseData") as mock_case_data,
            patch("app.means_test.api.EligibilityChecker") as mock_checker,
        ):
            mock_case_data.return_value.facts = Mock(has_partner=False)
            self._make_checker(mock_checker, EligibilityState.NO, False, True, True)

            api.check_eligibility()

            assert session["ineligible_reasons"] == [IneligibleReason.GROSS_INCOME]

    def test_disposable_income_reason_set(self, client):
        with (
            patch("app.means_test.api.CFEMeansTestPayload"),
            patch("app.means_test.api.create_update_case_reference"),
            patch("app.means_test.api.CaseData") as mock_case_data,
            patch("app.means_test.api.EligibilityChecker") as mock_checker,
        ):
            mock_case_data.return_value.facts = Mock(has_partner=False)
            self._make_checker(mock_checker, EligibilityState.NO, True, False, True)

            api.check_eligibility()

            assert session["ineligible_reasons"] == [IneligibleReason.DISPOSABLE_INCOME]

    def test_capital_reason_set(self, client):
        with (
            patch("app.means_test.api.CFEMeansTestPayload"),
            patch("app.means_test.api.create_update_case_reference"),
            patch("app.means_test.api.CaseData") as mock_case_data,
            patch("app.means_test.api.EligibilityChecker") as mock_checker,
        ):
            mock_case_data.return_value.facts = Mock(has_partner=False)
            self._make_checker(mock_checker, EligibilityState.NO, True, True, False)

            api.check_eligibility()

            assert session["ineligible_reasons"] == [IneligibleReason.CAPITAL]

    def test_multiple_reasons_set(self, client):
        with (
            patch("app.means_test.api.CFEMeansTestPayload"),
            patch("app.means_test.api.create_update_case_reference"),
            patch("app.means_test.api.CaseData") as mock_case_data,
            patch("app.means_test.api.EligibilityChecker") as mock_checker,
        ):
            mock_case_data.return_value.facts = Mock(has_partner=False)
            self._make_checker(mock_checker, EligibilityState.NO, False, False, False)

            api.check_eligibility()

            assert session["ineligible_reasons"] == [
                IneligibleReason.GROSS_INCOME,
                IneligibleReason.DISPOSABLE_INCOME,
                IneligibleReason.CAPITAL,
            ]

    def test_has_partner_set_on_session_when_ineligible(self, client):
        with (
            patch("app.means_test.api.CFEMeansTestPayload"),
            patch("app.means_test.api.create_update_case_reference"),
            patch("app.means_test.api.CaseData") as mock_case_data,
            patch("app.means_test.api.EligibilityChecker") as mock_checker,
        ):
            mock_case_data.return_value.facts = Mock(has_partner=True)
            self._make_checker(mock_checker, EligibilityState.NO, False, True, True)

            api.check_eligibility()

            assert session["has_partner"] is True
