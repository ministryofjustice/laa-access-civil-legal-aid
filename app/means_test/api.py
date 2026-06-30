from app.api import cla_backend
from flask import session
from logging import getLogger
from app.means_test.libs.eligibility_calculator.calculator import EligibilityChecker
from app.means_test.constants import EligibilityState
from app.constants.means_tests import IneligibleReason
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


def check_eligibility(payload: CFEMeansTestPayload | None = None) -> EligibilityState:
    if payload is None:
        payload = CFEMeansTestPayload()
        payload.update_from_session()

    # This is to save the case reference needed for backend
    create_update_case_reference()

    case_data = CaseData(**payload)
    eligibility_checker = EligibilityChecker(case_data)
    result, gross_ok, disp_ok, cap_ok = eligibility_checker.is_eligible_with_reasons()

    reasons: list[str] = []
    if result == EligibilityState.NO:
        if gross_ok is False:
            reasons.append(IneligibleReason.GROSS_INCOME)
        if disp_ok is False:
            reasons.append(IneligibleReason.DISPOSABLE_INCOME)
        if cap_ok is False:
            reasons.append(IneligibleReason.CAPITAL)

        session["ineligible_reasons"] = reasons
        session["has_partner"] = bool(getattr(case_data.facts, "has_partner", False))
    return result


def create_update_case_reference():
    """Create or update a backend case reference."""
    payload = MeansTestPayload()
    payload.update_from_session()
    update_means_test(payload)
