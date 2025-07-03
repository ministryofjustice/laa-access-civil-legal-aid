from flask_babel import lazy_gettext as _
from app.contact.forms import BaseForm
from app.contact.constants import CONTACT_PREFERENCE, NO_SLOT_CONTACT_PREFERENCE
from app.contact.widgets import ContactRadioInput
from wtforms import RadioField
from wtforms.validators import InputRequired
from flask import session


class OptionForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._adjust_contact_options_for_availability(session["contact"].time_slots)

    def _adjust_contact_options_for_availability(self, slots):
        """Remove callback option if no slots are available"""
        if len(slots) < 1:
            self.contact_type.choices = NO_SLOT_CONTACT_PREFERENCE

    title = _("Choose an option for your appointment")
    template = "contact/choose-an-option.html"
    url = "option-for-appointment"

    contact_type = RadioField(
        _(""),
        widget=ContactRadioInput(
            is_inline=False, choice_hint={"call": _("This is an 0345 number - there might be a call charge.")}
        ),
        choices=CONTACT_PREFERENCE,
        validators=[InputRequired(message=_("Select an option for your appointment"))],
    )
