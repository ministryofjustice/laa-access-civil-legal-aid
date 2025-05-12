from flask import current_app
from urllib.parse import urlencode, urljoin


def kwargs_to_urlparams(**kwargs: str) -> str:
    """
    Convert keyword arguments to URL parameters, filtering out None values.

    Args:
        **kwargs: Keyword arguments to convert to URL parameters.

    Returns:
        str: URL-encoded parameter string.
    """
    # Filter out None values
    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
    return urlencode(filtered_kwargs, doseq=True)


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
        params["categories"] = category
        if secondary_category:
            params["sub-category"] = secondary_category

    if params:
        return f"{base_url}?{urlencode(params)}"
    return base_url
