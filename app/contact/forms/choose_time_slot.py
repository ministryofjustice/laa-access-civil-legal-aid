from flask_babel import lazy_gettext as _
from app.contact.forms import BaseForm
from wtforms import RadioField
from wtforms.validators import InputRequired
from flask import session


class ChooseTimeSlotForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_time_slot_choices()

    def _set_time_slot_choices(self):
        """Set time slot choices based on session data"""
        time_slots = session["contact"].time_slots

        if not time_slots:
            self.time_slot.choices = []
            return

        # Group time slots by date for calendar display
        choices = []
        for slot in time_slots:
            # slot is already a datetime object
            try:
                value = slot.isoformat()
                label = f"{slot.strftime('%A %d %B %Y')} at {slot.strftime('%H:%M')}"
                choices.append((value, label))
            except (ValueError, AttributeError):
                # Fallback for unexpected formats
                choices.append((str(slot), str(slot)))

        self.time_slot.choices = choices

    def get_calendar_data(self):
        """Transform time slots into calendar format"""
        time_slots = session["contact"].time_slots

        if not time_slots:
            return {}

        calendar_data = {}
        has_sunday_slots = False

        # Check if any slots are on Sunday
        for slot in time_slots:
            if slot.weekday() == 6:  # Sunday is 6 in Python weekday()
                has_sunday_slots = True
                break

        for slot in time_slots:
            try:
                month_key = slot.strftime("%B %Y")  # E.g. September 2025
                date_key = slot.date()

                if month_key not in calendar_data:
                    calendar_data[month_key] = {}

                if date_key not in calendar_data[month_key]:
                    calendar_data[month_key][date_key] = []

                calendar_data[month_key][date_key].append({"time": slot.strftime("%H:%M"), "value": slot.isoformat()})

            except (ValueError, AttributeError):
                continue

        return {"calendar_data": calendar_data, "has_sunday_slots": has_sunday_slots}

    @classmethod
    def should_show(cls) -> bool:
        """Show this form only if callback option was selected and time slots exist"""
        contact = session["contact"]
        forms_data = contact.forms
        choose_option_data = forms_data.get("choose_an_option", {})

        # Only show if user selected callback option
        if choose_option_data.get("contact_type") != "callback":
            return False

        # Only show if time slots are available
        time_slots = contact.time_slots
        return len(time_slots) > 0

    title = _("Choose a time for your callback")
    template = "contact/choose-time-slot.html"
    url = "choose-time-slot"

    time_slot = RadioField(
        title,
        choices=[],  # Set dynamically in __init__
        validators=[InputRequired(message=_("Select a time for your callback"))],
    )
