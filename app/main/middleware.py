from app.main import bp


@bp.after_app_request
def add_noindex_header(response):
    """Add a noindex header to all responses, to disallow search engines from indexing the page."""
    response.headers["X-Robots-Tag"] = "noindex"
    return response


# Prevents the webbrowser from caching
@bp.after_app_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
