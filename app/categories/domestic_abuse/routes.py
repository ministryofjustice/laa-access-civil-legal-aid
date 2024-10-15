from app.categories.domestic_abuse import bp
from flask import render_template, url_for, redirect
from app.categories.domestic_abuse.forms import AreYouAtRiskOfHarmForm


@bp.route("")
def index():
    return render_template(
        "domestic-abuse.html",
        back_link=url_for("categories.index"),
    )


@bp.route("/protect-you-and-your-children", methods=["GET", "POST"])
def are_you_at_immediate_risk_of_harm():
    form = AreYouAtRiskOfHarmForm()

    if form.validate_on_submit():
        if form.question.data == "yes":
            return redirect("https://checklegalaid.service.gov.uk/contact")

    return render_template(
        "question-page.html",
        form=form,
        back_link=url_for("categories.domestic_abuse.index"),
    )
