from flask_babel import lazy_gettext as _
from govuk_frontend_wtf.wtforms_widgets import GovTextInput, GovSelect, GovTextArea
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, TextAreaField
from wtforms.validators import InputRequired, Optional, Email, Length

from app.contact.forms import BaseForm


class BookingForm(BaseForm):
    template = "contact/booking.html"
    title = _("Book an appointment with Civil Legal Advice")

    full_name = StringField(
        _("Your full name"),
        widget=GovTextInput(),
        validators=[
            InputRequired(message=_("Enter your name")),
        ],
    )

    email = StringField(
        _("Email address (optional)"),
        widget=GovTextInput(),
        validators=[
            Length(max=255, message=_("Your email address must be 255 characters or less")),
            Email(message=_("Enter an email address in the correct format, like name@example.com")),
            Optional(),
        ],
    )

    postcode = StringField(
        _("Postcode (optional)"),
        widget=GovTextInput(),
    )
    address_finder = SelectField(_("Select an address"), choices=[""], widget=GovSelect(), validate_choice=False)
    street_address = TextAreaField(
        _("Enter your home address (optional)"),
        widget=GovTextArea(),
        validators=[
            Length(max=255, message=_("Your address must be 255 characters or less")),
            Optional(),
        ],
    )
