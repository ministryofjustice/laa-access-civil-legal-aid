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
        _(""),
        widget=ContactRadioInput(
            is_inline=False, choice_hint={"call": "This is an 0345 number - there might be a call charge."}
        ),
        choices=CONTACT_PREFERENCE,
        validators=[InputRequired(message=_("Select an option for your appointment"))],
    )
