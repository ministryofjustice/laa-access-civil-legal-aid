from app.categories.housing import bp
from flask import render_template, url_for


@bp.route("")
def index():
    return render_template(
        "categories/housing/index.html",
        back_link=url_for("categories.index"),
    )


@bp.route("/homelessness")
def homelessness():
    return render_template(
        "categories/housing/homelessness.html",
        back_link=url_for("categories.housing.index"),
    )


@bp.route("/eviction-told-to-leave-your-home")
def eviction():
    return render_template(
        "categories/housing/eviction.html",
        back_link=url_for("categories.housing.index"),
    )


@bp.route("/forced-to-sell-losing-home-you-own")
def forced_sale():
    return render_template(
        "categories/housing/forced-sale.html",
        back_link=url_for("categories.housing.index"),
    )


@bp.route("/repairs-health-and-safety")
def repairs():
    return render_template(
        "categories/housing/repairs.html",
        back_link=url_for("categories.housing.index"),
    )


@bp.route("/problems-with-council-housing")
def council_housing():
    return render_template(
        "categories/housing/council-housing.html",
        back_link=url_for("categories.housing.index"),
    )
