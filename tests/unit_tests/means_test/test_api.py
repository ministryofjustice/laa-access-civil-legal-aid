from unittest.mock import patch
import pytest
from app.means_test import api
from app.means_test.constants import EligibilityState
from app.config import MeansTestCalculator
from app.means_test.payload import CFEMeansTestPayload, MeansTestPayload


class TestLogCalculatorMismatch:
    def test_log_calculator_mismatch_logs_to_both_logger_and_sentry(self, client):
        with (
            patch("app.means_test.api.logger") as mock_logger,
            patch("app.means_test.api.sentry_sdk") as mock_sentry,
        ):
            cfe_payload = CFEMeansTestPayload()
            cla_backend_payload = MeansTestPayload()

            api._log_calculator_mismatch(EligibilityState.YES, EligibilityState.NO, cfe_payload, cla_backend_payload)

            expected_msg = (
                "Means test calculator results mismatch: CFE=EligibilityState.YES, CLA_Backend=EligibilityState.NO"
            )
            mock_logger.error.assert_called_once_with(expected_msg, exc_info=True)
            mock_sentry.set_tag.assert_called_once_with("error_type", "means_test_mismatch")
            mock_sentry.capture_message.assert_called_once_with(expected_msg, level="error")


class TestRunParallelEligibilityCheck:
    def test_run_parallel_check_matching_results_no_logging(self, client):
        with (
            patch("app.means_test.api.CFEMeansTestPayload"),
            patch("app.means_test.api.MeansTestPayload"),
            patch("app.means_test.api._check_cfe_eligibility", return_value=EligibilityState.YES),
            patch("app.means_test.api._check_cla_backend_eligibility", return_value=EligibilityState.YES),
            patch("app.means_test.api._log_calculator_mismatch") as mock_log_mismatch,
        ):
            result = api._run_parallel_eligibility_check(MeansTestCalculator.CFE)

            mock_log_mismatch.assert_not_called()
            assert result == EligibilityState.YES

    def test_run_parallel_check_mismatching_results_logs_mismatch(self, client):
        with (
            patch("app.means_test.api.CFEMeansTestPayload"),
            patch("app.means_test.api.MeansTestPayload"),
            patch("app.means_test.api._check_cfe_eligibility", return_value=EligibilityState.YES),
            patch("app.means_test.api._check_cla_backend_eligibility", return_value=EligibilityState.NO),
            patch("app.means_test.api._log_calculator_mismatch") as mock_log_mismatch,
        ):
            result = api._run_parallel_eligibility_check(MeansTestCalculator.CFE)

            mock_log_mismatch.assert_called_once()
            assert result == EligibilityState.YES

    def test_run_parallel_check_prefers_cla_backend_when_specified(self, client):
        with (
            patch("app.means_test.api.CFEMeansTestPayload"),
            patch("app.means_test.api.MeansTestPayload"),
            patch("app.means_test.api._check_cfe_eligibility", return_value=EligibilityState.YES),
            patch("app.means_test.api._check_cla_backend_eligibility", return_value=EligibilityState.NO),
            patch("app.means_test.api._log_calculator_mismatch") as mock_log_mismatch,
        ):
            result = api._run_parallel_eligibility_check(MeansTestCalculator.CLA_BACKEND)

            mock_log_mismatch.assert_called_once()
            assert result == EligibilityState.NO


class TestCheckEligibility:
    def test_check_eligibility_uses_cfe_when_configured_no_parallel(self, client):
        with (
            patch("app.means_test.api.current_app") as mock_app,
            patch("app.means_test.api._check_cfe_eligibility", return_value=EligibilityState.YES) as mock_cfe,
        ):
            mock_app.config = {
                "MEANS_TEST_CALCULATOR": MeansTestCalculator.CFE,
                "RUN_MEANS_TEST_CALCULATORS_IN_PARALLEL": False,
            }

            result = api.check_eligibility()

            mock_cfe.assert_called_once()
            assert result == EligibilityState.YES

    def test_check_eligibility_uses_cla_backend_when_configured_no_parallel(self, client):
        with (
            patch("app.means_test.api.current_app") as mock_app,
            patch("app.means_test.api._check_cla_backend_eligibility", return_value=EligibilityState.NO) as mock_cla,
        ):
            mock_app.config = {
                "MEANS_TEST_CALCULATOR": MeansTestCalculator.CLA_BACKEND,
                "RUN_MEANS_TEST_CALCULATORS_IN_PARALLEL": False,
            }

            result = api.check_eligibility()

            mock_cla.assert_called_once()
            assert result == EligibilityState.NO

    def test_check_eligibility_runs_parallel_cfe_when_configured(self, client):
        with (
            patch("app.means_test.api.current_app") as mock_app,
            patch(
                "app.means_test.api._run_parallel_eligibility_check", return_value=EligibilityState.YES
            ) as mock_parallel,
        ):
            mock_app.config = {
                "MEANS_TEST_CALCULATOR": MeansTestCalculator.CFE,
                "RUN_MEANS_TEST_CALCULATORS_IN_PARALLEL": True,
            }

            result = api.check_eligibility()

            mock_parallel.assert_called_once_with(MeansTestCalculator.CFE)
            assert result == EligibilityState.YES

    def test_check_eligibility_runs_parallel_cla_backend_when_configured(self, client):
        with (
            patch("app.means_test.api.current_app") as mock_app,
            patch(
                "app.means_test.api._run_parallel_eligibility_check", return_value=EligibilityState.NO
            ) as mock_parallel,
        ):
            mock_app.config = {
                "MEANS_TEST_CALCULATOR": MeansTestCalculator.CLA_BACKEND,
                "RUN_MEANS_TEST_CALCULATORS_IN_PARALLEL": True,
            }

            result = api.check_eligibility()

            mock_parallel.assert_called_once_with(MeansTestCalculator.CLA_BACKEND)
            assert result == EligibilityState.NO

    def test_check_eligibility_raises_error_for_unknown_config(self, client):
        with patch("app.means_test.api.current_app") as mock_app:
            mock_app.config = {"MEANS_TEST_CALCULATOR": "UNKNOWN_CALCULATOR"}

            with pytest.raises(ValueError, match="Unknown calculator"):
                api.check_eligibility()

    def test_check_eligibility_raises_error_when_calculator_not_configured(self, client):
        with patch("app.means_test.api.current_app") as mock_app:
            mock_app.config = {}

            with pytest.raises(ValueError, match="MEANS_TEST_CALCULATOR not configured"):
                api.check_eligibility()
