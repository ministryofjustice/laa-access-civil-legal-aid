from app.api import cla_backend
from flask import session


def update_means_test(form_data):
    means_test_endpoint = "checker/api/v1/eligibility_check/"

    ec_reference = session.get("reference")

    if ec_reference:
        print(form_data)
        form_data["reference"] = ec_reference
        cla_backend.patch(f"{means_test_endpoint}/{ec_reference}", json=form_data)
    else:
        print(form_data)
        response = cla_backend.post(means_test_endpoint, json=form_data)
        session["reference"] = response["reference"]
