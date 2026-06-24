from unittest.mock import patch
from app.means_test import api
from app.means_test.constants import EligibilityState


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
