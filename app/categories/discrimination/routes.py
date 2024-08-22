from app.categories.discrimination import bp
from flask import render_template, redirect, url_for, request, session
from app.categories.forms import (
    DiscriminationForm,
    DiscriminationWhyForm,
    DiscriminationQuestions,
)
from app.categories.utils import get_items_with_divisor, check_radio_field


@bp.get("/discrimination")
def index():
    change_answer = request.args.get("change")
    if "discrimination" in session and not change_answer:
        if "where" in session["discrimination"]:
            return redirect(
                url_for(
                    "categories.discrimination.protected_characteristics",
                    where=session["discrimination"]["where"],
                )
            )

    form = DiscriminationForm()

    items = get_items_with_divisor(form.question.choices)

    previous_answer = request.args.get("previous_answer")
    if previous_answer:
        items = check_radio_field(form.question, previous_answer, items)

    return render_template(
        "discrimination.html",
        form=form,
        items=items,
        back_link=url_for("categories.index"),
    )


@bp.get("/discrimination/<string:where>")
def protected_characteristics(where: str):
    change_answer = request.args.get("change", False)
    if "discrimination" in session and not change_answer:
        if "where" in session["discrimination"]:
            if "why" in session["discrimination"]:
                return redirect(
                    url_for(
                        "categories.discrimination.result",
                        where=session["discrimination"]["where"],
                        why=session["discrimination"]["why"],
                    )
                )
            return redirect(
                url_for(
                    "categories.discrimination.protected_characteristics",
                    where=session["discrimination"]["where"],
                )
            )

    form = DiscriminationWhyForm()

    if where not in DiscriminationForm().valid_choices:
        redirect(url_for("categories.discrimination.index"))

    items = get_items_with_divisor(form.question.choices)

    previous_answer = request.args.get("previous_answer")
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

    if "discrimination" not in session:
        session["discrimination"] = {}

    session["discrimination"]["where"] = where
    session["discrimination"]["why"] = why

    summary_form = DiscriminationQuestions().summary_form()

    return render_template(
        "review-your-answers.html",
        back_link=url_for(
            "categories.discrimination.protected_characteristics",
            where=where,
            previous_answer=why,
            change=True,
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


@bp.post("/discrimination/<string:where>")
def why_form(where):
    form = DiscriminationWhyForm()
    if form.validate_on_submit():
        return redirect(
            url_for(
                "categories.discrimination.result", where=where, why=form.question.data
            )
        )
