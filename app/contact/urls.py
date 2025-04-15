import logging
from flask import jsonify
from app.contact import bp
from app.contact.address_finder.widgets import FormattedAddressLookup
from app.contact.views import (
    ContactUs,
    ReasonForContacting,
    ConfirmationPage,
    FastTrackedContactUs,
    EligibleContactUsPage,
)


logger = logging.getLogger(__name__)


bp.add_url_rule(
    "/eligible",
    view_func=EligibleContactUsPage.as_view(
        "eligible", template="contact/eligible.html", attach_eligibility_data=True
    ),
)


bp.add_url_rule(
    "/reasons-for-contacting",
    view_func=ReasonForContacting.as_view("reasons_for_contacting"),
)


@bp.route("/addresses/<postcode>", methods=["GET"])
def geocode(postcode):
    """Lookup addresses with the specified postcode"""
    formatted_addresses = FormattedAddressLookup().by_postcode(postcode)
    response = [
        {"formatted_address": address} for address in formatted_addresses if address
    ]
    return jsonify(response)


bp.add_url_rule(
    "/contact-us",
    view_func=ContactUs.as_view("contact_us", attach_eligibility_data=False),
)
bp.add_url_rule(
    "/contact-us/fast-tracked",
    view_func=FastTrackedContactUs.as_view(
        "contact_us_fast_tracked", attach_eligibility_data=False
    ),
)
bp.add_url_rule("/confirmation", view_func=ConfirmationPage.as_view("confirmation"))
