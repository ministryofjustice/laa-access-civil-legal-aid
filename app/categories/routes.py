from app.categories import bp
from flask import render_template, redirect, url_for, request
from werkzeug.wrappers.response import Response
from app.categories.forms import QuestionForm
from app.categories.traversal import category_traversal
from app.categories.utils import (
    get_items_with_divisor,
    check_radio_field,
    flatten_paths,
)


@bp.route("/")
def index():
    return render_template("categories/index.html")


@bp.route("/more-problems")
def more_problems():
    return render_template("categories/more-problems.html")


@bp.get("/<path:path>")
def question_page(path):
    form_or_response: QuestionForm | Response = (
        category_traversal.get_onward_question_from_path(path)
    )

    if isinstance(form_or_response, Response):
        return form_or_response

    form: type[QuestionForm] = form_or_response(request.args)

    back_link: str = category_traversal.get_previous_page_from_path(path)

    if form.submit.data and form.validate():
        path += f"/{form.question.data}"
        return redirect(url_for("categories.question_page", path=path))

    previous_answer = request.args.get("previous_answer")

    items = None
    if form.show_or_divisor:
        items = get_items_with_divisor(form.question.choices)
    if previous_answer:
        items = check_radio_field(form.question, previous_answer, items)

    return render_template(
        "categories/question-page.html",
        form=form,
        items=items,
        back_link=back_link,
    )


@bp.get("/contact")
def contact():
    return redirect("127.0.0.1:5000/contact")


@bp.get("/domestic-abuse")
def domestic_abuse():
    return render_template(
        "categories/domestic-abuse.html",
        back_link=url_for("categories.index"),
    )


@bp.get("/routing-map")
def routing_map():
    routing_map = flatten_paths(category_traversal.map_routing_logic())
    return render_template("categories/traversal-debug.html", paths=routing_map)
