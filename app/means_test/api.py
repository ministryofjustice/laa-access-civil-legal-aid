from app.api import cla_backend
from flask import session, current_app
from logging import getLogger
import sentry_sdk
from app.config import MeansTestCalculator
from app.means_test.libs.eligibility_calculator.calculator import EligibilityChecker
from app.means_test.constants import EligibilityState
from app.means_test.libs.eligibility_calculator.models import CaseData
from app.means_test.payload import CFEMeansTestPayload, MeansTestPayload

logger = getLogger(__name__)


def update_means_test(payload):
    means_test_endpoint = "checker/api/v1/eligibility_check/"

    ec_reference = session.ec_reference

    if ec_reference:
        response = cla_backend.patch(f"{means_test_endpoint}{ec_reference}", json=payload)
        logger.info(f"Updated eligibility check with reference {ec_reference}.")
        return response
    else:
        response = cla_backend.post(means_test_endpoint, json=payload)
        session.ec_reference = response["reference"]
        logger.info(f"Created new eligibility check with reference {response['reference']}.")
        return response


def is_eligible(reference) -> EligibilityState:
    if not reference:
        raise ValueError("Eligibility reference cannot be empty")

    means_test_endpoint = "checker/api/v1/eligibility_check/"
    response = cla_backend.post(f"{means_test_endpoint}{reference}/is_eligible/", {})
    state = response["is_eligible"]
    logger.info(f"Eligibility check {reference}, has eligibility state: {state}.")
    return getattr(EligibilityState, state.upper(), EligibilityState.UNKNOWN)


def _check_cfe_eligibility(payload: CFEMeansTestPayload | None = None) -> EligibilityState:
    """Check eligibility using CFE means test."""
    if payload is None:
        payload = CFEMeansTestPayload()
        payload.update_from_session()

    case_data = CaseData(**payload)
    eligibility_checker = EligibilityChecker(case_data)
    result, *_ = eligibility_checker.is_eligible_with_reasons()

    return result


def _check_cla_backend_eligibility(payload: MeansTestPayload | None = None) -> EligibilityState:
    """Check eligibility using CLA backend."""
    if payload is None:
        payload = MeansTestPayload()
        payload.update_from_session()

    response = update_means_test(payload)
    reference = response["reference"]
    return is_eligible(reference)


def _log_calculator_mismatch(
    cfe_result: EligibilityState,
    cla_backend_result: EligibilityState,
    cfe_payload: CFEMeansTestPayload,
    cla_backend_payload: MeansTestPayload,
) -> None:
    """Log calculator result mismatch to both local logs and Sentry."""
    error_msg = f"Means test calculator results mismatch: CFE={cfe_result}, CLA_Backend={cla_backend_result}"
    logger.error(error_msg)

    sentry_sdk.set_tag("error_type", "means_test_mismatch")
    sentry_sdk.set_context(
        "means_test_results",
        {
            "cfe_result": cfe_result,
            "cla_backend_result": cla_backend_result,
        },
    )
    sentry_sdk.set_context("cfe_payload", dict(cfe_payload))
    sentry_sdk.set_context("cla_backend_payload", dict(cla_backend_payload))
    sentry_sdk.capture_message(error_msg, level="error")


def _run_parallel_eligibility_check(preferred_calculator: MeansTestCalculator) -> EligibilityState:
    """Run both calculators in parallel, log if they mismatch, and return the preferred result."""
    cfe_payload = CFEMeansTestPayload()
    cfe_payload.update_from_session()
    cfe_result = _check_cfe_eligibility(cfe_payload)

    cla_backend_payload = MeansTestPayload()
    cla_backend_payload.update_from_session()
    cla_backend_result = _check_cla_backend_eligibility(cla_backend_payload)

    if cfe_result != cla_backend_result:
        _log_calculator_mismatch(cfe_result, cla_backend_result, cfe_payload, cla_backend_payload)

    return cfe_result if preferred_calculator == MeansTestCalculator.CFE else cla_backend_result


def check_eligibility() -> EligibilityState:
    """Check eligibility using the configured means test calculator."""
    calculator_type = current_app.config.get("MEANS_TEST_CALCULATOR")

    if calculator_type is None:
        raise ValueError("MEANS_TEST_CALCULATOR not configured")

    if calculator_type not in [MeansTestCalculator.CFE, MeansTestCalculator.CLA_BACKEND]:
        valid_types = [e.value for e in MeansTestCalculator]
        raise ValueError(f"Unknown calculator: {calculator_type}. Valid: {valid_types}")

    run_in_parallel = current_app.config.get("RUN_CALCULATORS_IN_PARALLEL", True)

    if run_in_parallel:
        return _run_parallel_eligibility_check(calculator_type)

    if calculator_type == MeansTestCalculator.CFE:
        result = _check_cfe_eligibility()
        return result
    else:
        result = _check_cla_backend_eligibility()
        return result
