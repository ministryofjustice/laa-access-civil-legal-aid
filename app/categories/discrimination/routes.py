from app.categories.discrimination import bp
from flask import render_template, redirect, url_for, request, session
from app.categories.forms import (
    DiscriminationForm,
    DiscriminationWhyForm,
    DiscriminationQuestions,
)
from app.categories.utils import get_items_with_divisor, check_radio_field


@bp.get("/discrimination")
def index(selected_answer=None):
    form = DiscriminationForm()

    items = get_items_with_divisor(form.question.choices)

    session_answer = None
    if "discrimination" in session and "where" in session["discrimination"]:
        session_answer = session["discrimination"]["where"]
    previous_answer = (
        request.args.get("previous_answer") or selected_answer or session_answer
    )
    if previous_answer:
        items = check_radio_field(form.question, previous_answer, items)

    return render_template(
        "discrimination.html",
        form=form,
        items=items,
        back_link=url_for("categories.index"),
    )


@bp.get("/discrimination/<string:where>")
def protected_characteristics(where: str, selected_answer=None):
    form = DiscriminationWhyForm()

    if where not in DiscriminationForm().valid_choices:
        redirect(url_for("categories.discrimination.index"))

    items = get_items_with_divisor(form.question.choices)

    session_answer = None
    print(session)
    if "discrimination" in session and "where" in session["discrimination"]:
        session_answer = session["discrimination"]["why"]
    previous_answer = (
        request.args.get("previous_answer") or selected_answer or session_answer
    )
    if previous_answer:
        items = check_radio_field(form.question, previous_answer, items)

    return render_template(
        "discrimination_why.html",
        form=form,
        items=items,
        back_link=url_for("categories.discrimination.index", previous_answer=where),
    )


@bp.get("/discrimination/<string:where>/<string:why>")
def result(where: str, why: str):
    if where not in DiscriminationForm().valid_choices:
        return redirect(url_for("categories.discrimination.index"))

    if why not in DiscriminationWhyForm().valid_choices:
        return redirect(
            url_for("categories.discrimination.protected_characteristics", where=where)
        )

    change_answer = request.args.get("change")
    if change_answer:
        if change_answer == "where":
            return index(selected_answer=where)
        if change_answer == "why":
            return protected_characteristics(where, selected_answer=why)

    if "discrimination" not in session:
        session["discrimination"] = {}

    session["discrimination"]["where"] = where
    session["discrimination"]["why"] = why

    summary_form = DiscriminationQuestions().summary_form(where, why)

    return render_template(
        "review-your-answers.html",
        back_link=url_for(
            "categories.discrimination.protected_characteristics",
            where=where,
            previous_answer=why,
        ),
        summary_form=summary_form,
    )


@bp.post("/discrimination")
def where_form():
    form = DiscriminationForm()
    if form.validate_on_submit():
        return redirect(
            url_for(
                "categories.discrimination.protected_characteristics",
                where=form.question.data,
            )
        )
    return redirect(url_for("categories.discrimination.index"))


@bp.post("/discrimination/<string:where>")
def why_form(where):
    form = DiscriminationWhyForm()
    if form.validate_on_submit():
        return redirect(
            url_for(
                "categories.discrimination.result", where=where, why=form.question.data
            )
        )


@bp.post("/discrimination/<string:where>/<string:why>")
def change_answer(where, why):
    answer_to_change = request.args.get("change")

    form = None
    if answer_to_change == "where":
        form = DiscriminationForm()
        where = form.question.data
    if answer_to_change == "why":
        form = DiscriminationWhyForm()
        why = form.question.data

    if not form:
        raise Exception()

    if form.validate_on_submit():
        return redirect(
            url_for("categories.discrimination.result", where=where, why=why)
        )
