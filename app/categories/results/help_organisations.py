import requests
from flask import current_app


def get_help_organisations(category: str, **kwargs):
    if not isinstance(category, str):
        return []
    kwargs["article_category__name"] = (
        category.title()
    )  # CLA Backend requires the category name to be title case
    hostname = current_app.config["BACKEND_URL"]
    response = requests.get(
        url=f"{hostname}/checker/api/v1/organisation", params=kwargs
    ).json()
    return response["results"]
