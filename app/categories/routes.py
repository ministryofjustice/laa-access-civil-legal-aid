from app.categories import bp
from flask import render_template


@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/more-problems")
def more_problems():
    return render_template("more-problems.html")