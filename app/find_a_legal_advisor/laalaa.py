import requests
from flask import current_app
from urllib.parse import urlencode


def kwargs_to_urlparams(**kwargs):
    kwargs = dict(filter(lambda kwarg: kwarg[1], kwargs.items()))
    return urlencode(kwargs, True)


def laalaa_url(endpoint: str = "legal-advisers", **kwargs):
    laalaa_api_host = current_app.config["LAALAA_URL"]
    params = kwargs_to_urlparams(**kwargs)
    return f"{laalaa_api_host}/{endpoint}/?{params}"


def laalaa_search(**kwargs):
    try:
        response = requests.get(laalaa_url(**kwargs))
        return response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        raise e
