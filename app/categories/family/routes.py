from app.categories.family import bp
from flask import render_template, url_for


@bp.route("")
def index():
    return render_template(
        "categories/family.html",
        back_link=url_for("categories.index"),
    )
