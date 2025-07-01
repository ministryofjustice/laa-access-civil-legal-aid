from flask_babel import lazy_gettext as _
from app.contact.forms import BaseForm
from app.contact.constants import CONTACT_PREFERENCE, NO_SLOT_CONTACT_PREFERENCE
from app.contact.widgets import ContactRadioInput
from wtforms import RadioField
from wtforms.validators import InputRequired
from app.api import cla_backend


class OptionForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get the valid timeslots once from backend and cache them
        self.time_slots = cla_backend.get_time_slots(num_days=8)
        self.thirdparty_time_slots = cla_backend.get_time_slots(num_days=8, is_third_party_callback=True)
        self._adjust_contact_options_for_availability()

    def _adjust_contact_options_for_availability(self):
        """Remove callback option if no slots are available"""
        if len(self.time_slots) <= 1:
            self.contact_type.choices = NO_SLOT_CONTACT_PREFERENCE

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
