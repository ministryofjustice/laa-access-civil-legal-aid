from flask import current_app
from urllib.parse import urlencode


def kwargs_to_urlparams(**kwargs):
    kwargs = dict(filter(lambda kwarg: kwarg[1], kwargs.items()))
    return urlencode(kwargs, True)


def backend_url(endpoint: str, **kwargs):
    backend_host_url = current_app.config["CLA_BACKEND_URL"]
    api_route = "/checker/api/v1/"
    params = kwargs_to_urlparams(**kwargs)
    if params:
        return f"{backend_host_url}{api_route}{endpoint}?{params}"
    return f"{backend_host_url}{api_route}{endpoint}"
