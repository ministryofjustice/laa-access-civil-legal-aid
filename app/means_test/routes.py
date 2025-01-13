from flask import render_template, request, url_for, redirect
from app.means_test import bp
from app.means_test.forms.benefits import BenefitsForm, AdditionalBenefitsForm


@bp.get("/mean-test-review")
def review():
    return render_template(
        "means_test/review.html",
    )


@bp.route("/benefits", methods=["GET", "POST"])
def benefits():
    form = BenefitsForm(data=request.form)
    if form.is_submitted() and form.validate():
        payload = form.payload()["benefits"]
        if payload == ["other-benefit"]:
            return redirect(url_for("means_test.additional_benefits"))
        else:
            return redirect(url_for("means_test.review"))
    return render_template("means_test/benefits.html", form=form)


@bp.route("/additional-benefits", methods=["GET", "POST"])
def additional_benefits():
    form = AdditionalBenefitsForm(data=request.form)
    if form.is_submitted() and form.validate():
        return redirect(url_for("means_test.review"))

    return render_template("means_test/benefits.html", form=form)
