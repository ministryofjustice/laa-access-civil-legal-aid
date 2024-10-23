from app.categories.domestic_abuse import bp
from flask import render_template, url_for, flash
from app.categories.domestic_abuse.forms import AreYouAtRiskOfHarmForm


@bp.route("")
def index():
    return render_template(
        "categories/domestic-abuse.html",
        back_link=url_for("categories.index"),
    )


@bp.route("/protect-you-and-your-children", methods=["GET", "POST"])
def are_you_at_immediate_risk_of_harm():
    form = AreYouAtRiskOfHarmForm()

    if form.validate_on_submit():
        flash("End of prototype")

    return render_template(
        "categories/question-page.html",
        form=form,
        back_link=url_for("categories.domestic_abuse.index"),
    )
