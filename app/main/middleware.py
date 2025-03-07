from app.main import bp


@bp.after_app_request
def add_noindex_header(response):
    """Add a noindex header to all responses, to disallow search engines from indexing the page."""
    response.headers["X-Robots-Tag"] = "noindex"
    return response
