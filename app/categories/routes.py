from app.categories import bp
from flask import render_template, redirect, url_for, request
from app.categories.forms import DiscriminationForm, DiscriminationWhyForm
from app.categories.utils import get_items_with_divisor, check_radio_field


@bp.route("/")
def index():
    return render_template("main.html")


@bp.route("/children-families-relationships")
def children_families_relationships():
    return render_template("children-families-relationships.html")


@bp.route("/discrimination", methods=["GET", "POST"])
def discrimination():
    form = DiscriminationForm()
    if form.validate_on_submit():
        return redirect(
            url_for("categories.discrimination_why", where=form.question.data)
        )

    previous_answer = request.args.get("previous_answer")
    items = get_items_with_divisor(form.question.choices)
    if previous_answer:
        items = check_radio_field(form.question, previous_answer, items)

    return render_template(
        "discrimination.html",
        form=form,
        items=items,
        back_link=url_for("categories.index"),
    )


@bp.route("/discrimination/<string:where>", methods=["GET", "POST"])
def discrimination_why(where):
    valid_choices = [choice[0] for choice in DiscriminationForm().question.choices]
    if where not in valid_choices:
        return redirect(url_for("categories.discrimination"))

    form = DiscriminationWhyForm()
    if form.validate_on_submit():
        return redirect(
            url_for(
                "categories.discrimination_result", where=where, why=form.question.data
            )
        )

    previous_answer = request.args.get("previous_answer")
    items = get_items_with_divisor(form.question.choices)
    if previous_answer:
        items = check_radio_field(form.question, previous_answer, items)
    return render_template(
        "discrimination_why.html",
        form=form,
        items=items,
        back_link=url_for("categories.discrimination", previous_answer=where),
    )


@bp.route("/discrimination/<path:where>/<path:why>", methods=["GET", "POST"])
def discrimination_result(where, why):
    return render_template(
        "result.html",
        back_link=url_for(
            "categories.discrimination_why", where=where, previous_answer=why
        ),
    )


@bp.route("/why", methods=["GET", "POST"])
def why():
    form = DiscriminationWhyForm()
    if form.validate_on_submit():
        return redirect(url_for("categories.discrimination.why"))
    return render_template("discrimination_why.html", form=form)
