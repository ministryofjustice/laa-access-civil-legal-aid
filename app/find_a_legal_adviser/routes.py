from app.find_a_legal_adviser import bp
from flask import render_template, request, abort

from app.find_a_legal_adviser.categories import FALACategory
from app.find_a_legal_adviser.fala import create_fala_url


@bp.get("/find-a-legal-adviser")
def search():
    category: str | None = request.args.get("category", default=None)
    secondary_category: str | None = request.args.get(
        "secondary_category", default=None
    )

    if category is not None and not FALACategory.is_valid_category(category):
        return abort(404, f"Invalid category: {category}")

    if secondary_category is not None and not FALACategory.is_valid_category(
        secondary_category
    ):
        return abort(404, f"Invalid secondary category: {category}")

    fala_url = create_fala_url(category=category, secondary_category=secondary_category)
    return render_template("categories/fala-interstitial.html", fala_url=fala_url)
