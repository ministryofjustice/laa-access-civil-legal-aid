from flask_babel import lazy_gettext as _
from app.contact.forms import BaseForm
from app.contact.constants import (
    CONTACT_PREFERENCE,
)
from app.contact.widgets import ContactRadioInput
from wtforms import RadioField
from wtforms.validators import InputRequired


class OptionForm(BaseForm):
    title = _("Choose an option for your appointment")
    template = "contact/choose-an-option.html"
    url = "option-for-appointment"

    contact_type = RadioField(
        widget=ContactRadioInput(is_inline=False, heading_class="govuk-fieldset__legend--m"),
        choices=CONTACT_PREFERENCE,
        validators=[InputRequired(message=_("Tell us how we should get in contact"))],
    )
