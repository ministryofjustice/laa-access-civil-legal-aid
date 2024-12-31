import requests
from flask import current_app
from app.extensions import cache


@cache.memoize(timeout=86400)  # 1 day
def get_help_organisations(category: str, **kwargs):
    """Get help organisations for a given category, each unique set of arguments return value is cached for 24 hours.
    Args:
        category (str): An article category name
        kwargs: Any additional query parameters to pass to the backend
    Returns:
        List[str]: A list of help organisations
    """
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
