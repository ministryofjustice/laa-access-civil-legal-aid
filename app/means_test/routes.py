from flask import render_template, redirect, url_for
from app.means_test import bp
from app.means_test.forms import AboutYouForm


@bp.route("/about-you", methods=["GET", "POST"])
def about_you():
    form = AboutYouForm()

    if form.validate_on_submit():
        return redirect(url_for("means_test.about-your-income"))

    return render_template("means_test/about-you.html", form=form)
