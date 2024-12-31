import requests
from flask import current_app


def post_reasons_for_contacting(form=None, payload={}):
    hostname = current_app.config["CLA_BACKEND_URL"]
    payload = form.api_payload() if form else payload
    response = requests.post(
        url=f"{hostname}/checker/api/v1/reasons_for_contacting/", json=payload
    )
    return response
