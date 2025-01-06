from flask import render_template
from app.means_test import bp
from app.means_test.forms import AboutYouForm


@bp.get("/about-you")
def about_you():
    form = AboutYouForm()
    return render_template("means_test/about-you.html", form=form)
