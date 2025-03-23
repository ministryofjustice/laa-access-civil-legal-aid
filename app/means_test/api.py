from app.api import cla_backend
from flask import session
from app.means_test.constants import EligibilityState


def update_means_test(payload):
    means_test_endpoint = "checker/api/v1/eligibility_check/"

    ec_reference = session.get("ec_reference")

    if ec_reference:
        response = cla_backend.patch(
            f"{means_test_endpoint}{ec_reference}", json=payload
        )
        return response
    else:
        response = cla_backend.post(means_test_endpoint, json=payload)
        session["ec_reference"] = response["reference"]
        return response


def is_eligible(reference) -> EligibilityState:
    if not reference:
        raise ValueError("Eligibility reference cannot be empty")

    means_test_endpoint = "checker/api/v1/eligibility_check/"
    response = cla_backend.post(f"{means_test_endpoint}{reference}/is_eligible/", {})
    state = response["is_eligible"]
    return EligibilityState(state)
