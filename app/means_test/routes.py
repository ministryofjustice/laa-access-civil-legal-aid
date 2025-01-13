from flask import render_template
from app.means_test import bp
from app.means_test.forms import AboutYouForm
from app.means_test.api import update_means_test


@bp.route("/about-you", methods=["GET", "POST"])
def about_you():
    form = AboutYouForm()

    if form.validate_on_submit():
        update_means_test(form.payload_2())
        return "Done"

    return render_template("means_test/about-you.html", form=form)
