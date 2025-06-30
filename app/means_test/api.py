from app.api import cla_backend
from flask import session, current_app
from logging import getLogger
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


def _check_cfe_eligibility() -> EligibilityState:
    """Check eligibility using CFE means test."""
    payload = CFEMeansTestPayload()
    payload.update_from_session()

    case_data = CaseData(**payload)
    eligibility_checker = EligibilityChecker(case_data)
    eligibility_result, *_ = eligibility_checker.is_eligible_with_reasons()

    return eligibility_result


def _check_cla_backend_eligibility() -> EligibilityState:
    """Check eligibility using CLA backend."""
    payload = MeansTestPayload()
    payload.update_from_session()

    response = update_means_test(payload)
    return response["result"]


CALCULATOR_HANDLERS = {
    MeansTestCalculator.CFE: _check_cfe_eligibility,
    MeansTestCalculator.CLA_BACKEND: _check_cla_backend_eligibility,
}


def check_eligibility() -> EligibilityState:
    """Check eligibility using the configured means test calculator."""
    calculator_type = current_app.config.get("MEANS_TEST_CALCULATOR")

    match calculator_type:
        case MeansTestCalculator.CFE:
            return _check_cfe_eligibility()
        case MeansTestCalculator.CLA_BACKEND:
            return _check_cla_backend_eligibility()
        case None:
            raise ValueError("MEANS_TEST_CALCULATOR not configured")
        case _:
            valid_types = [e.value for e in MeansTestCalculator]
            raise ValueError(f"Unknown calculator: {calculator_type}. Valid: {valid_types}")
