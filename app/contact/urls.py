from app.contact import bp
from app.contact.forms import ReasonsForContactingForm, ContactUsForm
from app.contact.address_finder.widgets import FormattedAddressLookup
from app.api import cla_backend
from flask import request, redirect, url_for, render_template, Response, current_app
import json
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
    if form.validate_on_submit():
        payload = form.get_payload()
        result = cla_backend.post_case(payload=payload)
        logger.info("API Response: %s", result)
        return render_template("contact/contact.html", form=form)
        # return render_template("contact/confirmation.html")
    return render_template("contact/contact.html", form=form)


@bp.route("/confirmation", methods=["GET", "POST"])
def confirmation():
    return render_template("contact/confirmation.html")


@bp.route("/addresses/<postcode>", methods=["GET"])
def geocode(postcode):
    """Lookup addresses with the specified postcode"""
    key = current_app.config["OS_PLACES_API_KEY"]
    formatted_addresses = FormattedAddressLookup(key=key).by_postcode(postcode)
    response = [
        {"formatted_address": address} for address in formatted_addresses if address
    ]
    return Response(json.dumps(response), mimetype="application/json")
