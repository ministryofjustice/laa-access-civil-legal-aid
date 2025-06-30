from app.api import cla_backend
from flask import session
from logging import getLogger

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
