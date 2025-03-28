from app.api import cla_backend
from flask import session


def update_means_test(payload):
    means_test_endpoint = "checker/api/v1/eligibility_check/"

    ec_reference = session.get("ec_reference")

    if ec_reference:
        response = cla_backend.patch(f"{means_test_endpoint}{ec_reference}", json=payload)
        return response
    else:
        response = cla_backend.post(means_test_endpoint, json=payload)
        session["ec_reference"] = response["reference"]
        return response


def is_eligible(reference):
    means_test_endpoint = "checker/api/v1/eligibility_check/"
    response = cla_backend.post(f"{means_test_endpoint}{reference}/is_eligible/")
    return response["is_eligible"]
