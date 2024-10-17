from app.categories.discrimination import bp
from flask import render_template, url_for, flash, redirect
from app.categories.discrimination.forms import (
    DiscriminationWhereForm,
    DiscriminationWhyForm,
)
from app.categories.utils import get_items_with_divisor


@bp.route("", methods=["GET", "POST"])
def where_did_the_discrimination_happen():
    form = DiscriminationWhereForm()

    items = get_items_with_divisor(form.question.choices)

    if form.validate_on_submit():
        if form.question.data == "work":
            return redirect(
                url_for(
                    "categories.discrimination.why_were_you_treated_differently",
                    where=form.question.data,
                )
            )
        flash("End of prototype")

    return render_template(
        "question-page.html",
        form=form,
        items=items,
        back_link=url_for("categories.index"),
    )


@bp.route("/<string:where>", methods=["GET", "POST"], defaults={"where": "work"})
def why_were_you_treated_differently(where):
    form = DiscriminationWhyForm()

    items = get_items_with_divisor(form.question.choices)

    if form.validate_on_submit():
        if form.question.data == "disability":
            return redirect(
                "https://checklegalaid.service.gov.uk/legal-aid-available?hlpas=no"
            )
        flash("End of prototype")

    return render_template(
        "question-page.html",
        form=form,
        items=items,
        back_link=url_for(
            "categories.discrimination.where_did_the_discrimination_happen"
        ),
    )
