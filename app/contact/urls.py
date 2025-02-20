from app.contact import bp
from app.contact.address_finder.widgets import FormattedAddressLookup
from app.contact.views import ContactUs, ReasonForContacting
from flask import (
    render_template,
    Response,
    current_app,
)
import json
import logging

logger = logging.getLogger(__name__)


bp.add_url_rule(
    "/reasons-for-contacting",
    view_func=ReasonForContacting.as_view("reasons_for_contacting"),
)


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


bp.add_url_rule(
    "/contact-us",
    view_func=ContactUs.as_view("contact_us", attach_eligiblity_data=False),
)

bp.add_url_rule(
    "/eligible",
    view_func=ContactUs.as_view(
        "eligible", template="contact/eligible.html", attach_eligiblity_data=True
    ),
)
