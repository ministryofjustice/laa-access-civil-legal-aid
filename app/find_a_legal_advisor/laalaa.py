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


def laalaa_search(endpoint="legal-advisers", **kwargs):
    """
    Sends a request to the LAA Legal Advisors API with the given parameters.

    Args:
        endpoint(str): The endpoint to send the request to, defaults to legal-advisers
        **kwargs: The parameters to send with the request
    """
    response = requests.get(laalaa_url(endpoint, **kwargs))
    return response.json()


def get_category_name(category_code: str):
    """
    Returns the category associated with a given category code.

    Args:
        category_code (str): The code to look up

    Returns:
        str: The corresponding category name if found, None if not found
    """
    from app.find_a_legal_advisor import (
        bp,
    )  # We import this here as the blueprint needs to be initialised to contain category information

    category_code = (
        category_code.upper()
    )  # Convert to uppercase to make search case-insensitive
    for category in bp.categories:
        if category["code"] == category_code:
            return category["name"]
    return None


def is_valid_category_code(category_code: str | None):
    from app.find_a_legal_advisor import bp

    if not isinstance(category_code, str):
        return False

    category_code = (
        category_code.upper()
    )  # Convert to uppercase to make search case-insensitive
    for category in bp.categories:
        if category["code"] == category_code:
            return True
    return False
