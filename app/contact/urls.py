from app.contact import bp
from app.contact.forms import ReasonsForContactingForm, ContactUsForm
from app.api import cla_backend
from flask import request, redirect, url_for, render_template
import logging

logger = logging.getLogger(__name__)


@bp.route("/reasons-for-contacting", methods=["GET", "POST"])
def reasons_for_contacting():
    form = ReasonsForContactingForm()
    if request.method == "GET":
        form.referrer.data = request.referrer or "Unknown"
    if form.validate_on_submit():
        result = cla_backend.post_reasons_for_contacting(form=form)
        next_step = form.next_step_mapping.get("*")
        logger.info("API Response: %s", result)
        return redirect(url_for(next_step))
    return render_template("contact/rfc.html", form=form)


@bp.route("/contact-us", methods=["GET", "POST"])
def contact_us():
    form = ContactUsForm()
    return render_template("contact/contact.html", form=form)
