from app.categories import bp
from flask import render_template, session


@bp.route("/")
def index():
    session["discrimination"] = {}
    return render_template("main.html")


@bp.route("/more-problems")
def more():
    return render_template("more-problems.html")


@bp.route("/children-families-relationships")
def children_families_relationships():
    return render_template("children-families-relationships.html")


@bp.route("/result")
def result():
    session["discrimination"] = {}
    return render_template("result.html")
