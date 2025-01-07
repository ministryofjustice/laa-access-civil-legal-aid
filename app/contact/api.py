import requests
from app.main.api import backend_url


def post_reasons_for_contacting(form=None, payload={}):
    url = backend_url(endpoint="reasons_for_contacting/")
    payload = form.api_payload() if form else payload
    response = requests.post(url=url, json=payload)
    return response
