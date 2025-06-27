from flask import redirect, url_for, request
from app.main import bp

REDIRECT_MAP = {
    "/scope/diagnosis": "categories.index",
    "/accessibility-statement": "main.accessibility",
    "/contact": "contact_backup.contact_us",
    "/scope/refer/domestic-abuse": "categories.domestic_abuse.cannot_find_your_problem",
    "/scope/refer/discrimination": "categories.discrimination.cannot_find_your_problem",
    "/scope/refer/education": "categories.send.cannot_find_your_problem",
    "/scope/refer/family": "categories.family.cannot_find_your_problem",
    "/scope/refer/housing": "categories.housing.cannot_find_your_problem",
    "/scope/refer/immigration-and-asylum": "categories.asylum_immigration.cannot_find_your_problem",
    "/scope/refer/debt": "find-a-legal-adviser.search",
    "/scope/refer/welfare-benefits": "find-a-legal-adviser.search",
    "/scope/refer/any-other-problem": "categories.results.cannot_find_your_problem",
}

FALA_REDIRECT_MAP = {
    "clinneg": {"category": "med"},
    "commcare": {"category": "com"},
    "traffickingandslavery": {"category": "immas"},
    "mentalhealth": {"category": "mhe", "secondary_category": "com"},
    "publiclaw": {"category": "pub"},
    "aap": {"category": "aap"},
    "other": {"category": ""},
}


def create_redirect_handler(destination):
    """Returns a function that redirects to the given destination."""

    def redirect_view():
        return redirect(url_for(destination), code=301)

    return redirect_view


# Create endpoints for the old service
for old_path, new_destination in REDIRECT_MAP.items():
    endpoint_name = f"redirect_{old_path.strip('/').replace('/', '_')}"
    bp.add_url_rule(
        old_path,
        endpoint=endpoint_name,
        view_func=create_redirect_handler(new_destination),
    )


@bp.get("/scope/diagnosis/<path:path>")
def handle_scope_diagnosis_redirect(path):
    """Redirects any /scope/diagnosis* path to categories.index"""
    return redirect(url_for("main.session_expired"), code=301)


@bp.route("/scope/refer/legal-adviser")
def handle_fala_redirect():
    """Handles FALA redirects dynamically based on query parameters."""
    category = request.args.get("category")
    if category in FALA_REDIRECT_MAP:
        return redirect(
            url_for(
                "find-a-legal-adviser.search",
                category=FALA_REDIRECT_MAP[category].get("category"),
                secondary_category=FALA_REDIRECT_MAP[category].get("secondary_category"),
            ),
            code=301,
        )

    return redirect(url_for("find-a-legal-adviser.search"), code=301)
