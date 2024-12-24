from urllib.parse import urlencode
import requests
from flask import current_app


def kwargs_to_urlparams(**kwargs):
    kwargs = dict(filter(lambda kwarg: kwarg[1], kwargs.items()))
    return urlencode(kwargs, True)


def backend_url(endpoint: str = "organisation", **kwargs):
    backend_api_host = current_app.config["BACKEND_URL"]
    params = kwargs_to_urlparams(**kwargs)
    return f"{backend_api_host}/checker/api/v1/{endpoint}/?{params}"


def get_help_organisations(category: str, **kwargs):
    if isinstance(category, str):
        category = (
            category.title()
        )  # CLA Backend requires the category name to be title case
    response = requests.get(
        backend_url(article_category__name=category, **kwargs)
    ).json()
    return response["results"]
