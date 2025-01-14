from flask import render_template, request
from app.means_test import bp
from app.means_test.forms.property import PropertyForm


@bp.get("/mean-test-review")
def review():
    return "I am a holding page"


@bp.route("/property", methods=["GET", "POST"])
def property():
    form = PropertyForm(data=request.form)
    return render_template("means_test/property.html", form=form)
