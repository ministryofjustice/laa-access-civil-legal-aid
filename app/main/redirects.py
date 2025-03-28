from flask import redirect, url_for, abort, request
from app.main import bp

REDIRECT_MAP = {
    "/scope/diagnosis": "categories.index",
    "/accessibility-statement": "main.accessibility",
    "/contact": "contact.contact_us",
    "/scope/refer/domestic-abuse": "categories.domestic_abuse.cannot_find_your_problem",
    "/scope/refer/discrimination": "categories.discrimination.cannot_find_your_problem",
    "/scope/refer/education": "categories.send.cannot_find_your_problem",
    "/scope/refer/family": "categories.family.cannot_find_your_problem",
    "/scope/refer/housing": "categories.housing.cannot_find_your_problem",
    "/scope/refer/immigration-and-asylum": "categories.asylum_immigration.cannot_find_your_problem",
    "/scope/refer/debt": "find-a-legal-adviser.search",
    "/scope/refer/welfare-benefits": "find-a-legal-adviser.search",
    "/scope/refer/any-other-problem": "categories.results.refer",
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


@bp.route("/<path:path>")
def handle_redirects(path):
    """Redirects from old check URL to new access URL, else returns 404"""
    requested_path = f"/{path}"

    # Handle FALA redirects
    if path.startswith("scope/refer/legal-adviser"):
        category = request.args.get("category")
        if category in FALA_REDIRECT_MAP:
            return redirect(
                url_for(
                    "find-a-legal-adviser.search",
                    category=FALA_REDIRECT_MAP[category].get("category"),
                    secondary_category=FALA_REDIRECT_MAP[category].get(
                        "secondary_category"
                    ),
                ),
                code=301,
            )

    # Handle other redirects
    if requested_path in REDIRECT_MAP:
        return redirect(url_for(REDIRECT_MAP[requested_path]), code=301)
    elif requested_path.startswith("/scope/diagnosis"):
        return redirect(url_for("categories.index"), code=301)

    return abort(404)
