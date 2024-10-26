from werkzeug.exceptions import NotFound

from app.categories import bp
from flask import render_template, redirect, url_for, request, abort
from app.categories.traversal import category_traversal, NavigationResult
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
    print(category_traversal.get_question_answer_map(path))
    try:
        path_result: NavigationResult = category_traversal.navigate_path(path)
    except NotFound:
        abort(404)

    if path_result.internal_redirect:
        return redirect(url_for(path_result.internal_redirect))

    if path_result.external_redirect:
        return path_result.external_redirect

    form = path_result.question_form(request.args)
    back_link: str = category_traversal.get_previous_page_url(path)

    if form.submit.data and form.validate():
        path += f"/{form.question.data}"
        return redirect(url_for("categories.question_page", path=path))

    previous_answer = request.args.get("previous_answer")

    # TODO: Make an override of the GOV.UK WTForms radio field class to support divisors.
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
