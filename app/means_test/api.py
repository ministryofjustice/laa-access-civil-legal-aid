from app.api import cla_backend
from flask import session, url_for, redirect


def update_means_test(payload):
    means_test_endpoint = "checker/api/v1/eligibility_check/"

    ec_reference = session.get("reference")

    if ec_reference:
        print(payload)
        response = cla_backend.patch(
            f"{means_test_endpoint}{ec_reference}", json=payload
        )
        return response
    else:
        print(payload)
        response = cla_backend.post(means_test_endpoint, json=payload)
        session["reference"] = response["reference"]
        session["name"] = "Ben"
        print(session)
        return redirect(url_for(("categories.results.in_scope")))


def is_eligible(reference):
    means_test_endpoint = "checker/api/v1/eligibility_check/"
    response = cla_backend.post(f"{means_test_endpoint}{reference}/is_eligible/")
    return response["is_eligible"]
