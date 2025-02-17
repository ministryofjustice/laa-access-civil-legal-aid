from app.contact import bp
from app.contact.forms import ReasonsForContactingForm, ContactUsForm
from app.contact.address_finder.widgets import FormattedAddressLookup
from app.contact.notify.api import (
    NotifyEmailOrchestrator,
    create_and_send_confirmation_email,
)
from app.api import cla_backend
from flask import (
    request,
    redirect,
    url_for,
    render_template,
    Response,
    current_app,
    session,
)
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
        if result and "reference" in result:
            session[form.MODEL_REF_SESSION_KEY] = result["reference"]
        return redirect(url_for(next_step))
    return render_template("contact/rfc.html", form=form)


@bp.route("/contact-us", methods=["GET", "POST"])
def contact_us():
    form = ContactUsForm()
    if form.validate_on_submit():
        # Add notes from tell us more about your problem
        payload = form.get_payload()
        # Catches duplicate case exceptions and redirect to error page
        try:
            result = cla_backend.post_case(payload=payload)
        except Exception as e:
            if hasattr(e, "response") and e.response.status_code == 500:
                return render_template("components/error_page.html")
        logger.info("API Response: %s", result)
        callback = ["callback", "thirdparty"]
        session["callback_requested"] = (
            True if form.data.get("contact_type") in callback else False
        )
        session["contact_type"] = form.data.get("contact_type")
        requires_action_at, formatted_time = ContactUsForm.get_callback_time(form)
        session["formatted_time"] = formatted_time
        email = form.get_email()
        if email:
            govuk_notify = NotifyEmailOrchestrator()
            data = form.data
            data["email"] = email
            create_and_send_confirmation_email(govuk_notify, data)
        if ReasonsForContactingForm.MODEL_REF_SESSION_KEY in session:
            cla_backend.update_reasons_for_contacting(
                session[ReasonsForContactingForm.MODEL_REF_SESSION_KEY],
                payload={"case": session["reference"]},
            )
            del session[ReasonsForContactingForm.MODEL_REF_SESSION_KEY]
        return render_template("contact/confirmation.html", data=session["reference"])
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
