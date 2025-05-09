from flask import current_app
from urllib.parse import urlencode, urljoin


def create_fala_url(
    category: str | None = None,
    secondary_category: str | None = None,
) -> str:
    """
    Create a URL for the single page Find a Legal Adviser view with optional category parameters.

    Args:
        category: Primary category (optional).
        secondary_category: Secondary category (optional, only used if category is provided).

    Returns:
        str: The complete URL to the FALA endpoint with parameters.

    Raises:
        KeyError: If FALA_URL is not configured in the Flask application.
    """
    try:
        fala_host = current_app.config["FALA_URL"]
    except KeyError:
        raise KeyError("FALA_URL not configured")

    check_endpoint = "check"
    base_url = urljoin(fala_host, check_endpoint)

    params: dict[str, str] = {}
    if category:
        params["categories"] = category.lower()
        if secondary_category:
            params["sub-category"] = secondary_category.lower()

    if params:
        return f"{base_url}?{urlencode(params, doseq=True)}"
    return base_url
