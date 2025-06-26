import json
from flask_wtf import FlaskForm
from flask import request, session
from wtforms import (
    SelectMultipleField,
    HiddenField,
    StringField,
    RadioField,
    TextAreaField,
    SelectField,
)
from govuk_frontend_wtf.wtforms_widgets import (
    GovSubmitInput,
    GovTextInput,
    GovTextArea,
    GovSelect,
)

from app.contact_backup.widgets import (
    ContactRadioInput,
    ContactCheckboxInput,
    ContactSelectField,
    ContactTextInput,
)
from wtforms.fields import SubmitField
from app.categories.widgets import CategoryCheckboxInput
from app.contact_backup.constants import (
    LANG_CHOICES,
    THIRDPARTY_RELATIONSHIP_CHOICES,
    CONTACT_PREFERENCE,
    NO_SLOT_CONTACT_PREFERENCE,
)
from flask_babel import lazy_gettext as _
from wtforms.validators import InputRequired, Length, Optional, Email
from app.main import get_locale
from app.contact_backup.validators import (
    ValidateDayTime,
)
from app.means_test.validators import ValidateIf, ValidateIfType
from app.api import cla_backend
from datetime import datetime, timedelta
from babel.dates import format_date


class ReasonsForContactingForm(FlaskForm):
    MODEL_REF_SESSION_KEY = "reason_for_contact"
    next_step_mapping = {
        "*": "contact.contact_us",
    }

    title = _("Why do you want to contact Civil Legal Advice?")

    reasons = SelectMultipleField(
        title,
        widget=CategoryCheckboxInput(hint_text=_("Select all that apply")),
        choices=[
            ("CANT_ANSWER", _("I don’t know how to answer a question")),
            ("MISSING_PAPERWORK", _("I don’t have the paperwork I need")),
            (
                "PREFER_SPEAKING",
                _("I’d prefer to speak to someone"),
            ),
            ("DIFFICULTY_ONLINE", _("I have trouble using online services")),
            ("HOW_SERVICE_HELPS", _("I don’t understand how this service can help me")),
            (
                "AREA_NOT_COVERED",
                _("My problem area isn’t covered"),
            ),
            ("PNS", _("I’d prefer not to say")),
            ("OTHER", _("Another reason")),
        ],
    )

    referrer = HiddenField()
    save = SubmitField(_("Continue to contact CLA"), widget=GovSubmitInput())

    def api_payload(self):
        return {
            "reasons": [{"category": category} for category in self.reasons.data],
            "other_reasons": "",
            "user_agent": request.headers.get("User-Agent") or "Unknown",
            "referrer": self.referrer.data or "Unknown",
        }


class ContactUsForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(ContactUsForm, self).__init__(*args, **kwargs)

        if self.adaptations.data is None:  # Data defaults to None when form is first loaded
            self.adaptations.data = ["welsh"] if get_locale().startswith("cy") else []

        # Get the valid timeslots once from backend and cache them
        self.time_slots = cla_backend.get_time_slots(num_days=8)
        self.thirdparty_time_slots = cla_backend.get_time_slots(num_days=8, is_third_party_callback=True)

        self._setup_callback_time_choices()

    def _setup_callback_time_choices(self):
        """Setup callback day time select field choices based on the available slots"""
        today: str = datetime.today().strftime("%Y-%m-%d")

        self.time_slots = self._format_slots_by_day(self.time_slots, locale=get_locale())
        self.thirdparty_time_slots = self._format_slots_by_day(self.thirdparty_time_slots)

        # Setup today's time choices
        self._setup_today_choices(today)

        # Setup other days choices
        self._setup_other_days_choices(today)

        # Setup choices for previously selected days
        self._setup_selections_for_chosen_days()

        # Hide callback option if there are no slots available
        self._adjust_contact_options_for_availability()

    def _format_slots_by_day(self, slots, locale="en"):
        slots_by_day = {}

        for slot in slots:
            date_str = slot.date().strftime("%Y-%m-%d")

            slots_by_day.setdefault(date_str, [])
            seperator = "to"
            am_time_suffix = "am"
            pm_time_suffix = "pm"
            if locale == "cy":
                seperator = "i"
                am_time_suffix = "yb"
                pm_time_suffix = "yh"
            slots_by_day[date_str].append(
                [
                    slot.strftime("%H%M"),
                    f"{slot.strftime('%I.%M%p').lstrip('0').replace('.00', '').replace('AM', am_time_suffix).replace('PM', pm_time_suffix)} {seperator} {(slot + timedelta(minutes=30)).strftime('%I.%M%p').lstrip('0').replace('.00', '').replace('AM', am_time_suffix).replace('PM', pm_time_suffix)}",
                ]
            )

        return slots_by_day

    def _setup_today_choices(self, today):
        """Setup today's time slot choices"""
        # Regular callback
        today_slots = self.time_slots.get(today, [])
        self.call_today_time.choices.extend(today_slots)
        if not today_slots:
            self.time_to_call.choices = ["Call on another day"]

        # Third-party callback
        thirdparty_today_slots = self.thirdparty_time_slots.get(today, [])
        self.thirdparty_call_today_time.choices.extend(thirdparty_today_slots)
        if not thirdparty_today_slots:
            self.thirdparty_time_to_call.choices = ["Call on another day"]

    def _setup_other_days_choices(self, today: str):
        """Setup choices for days other than today"""
        # Regular callback setup
        regular_upcoming_days = sorted([day for day in self.time_slots.keys() if day != today])
        regular_day_choices = [
            (
                day,
                format_date(
                    datetime.strptime(day, "%Y-%m-%d"),
                    format="EEE d MMM",
                    locale=get_locale(),
                ),
            )
            for day in regular_upcoming_days
        ]

        self.call_another_day.choices.extend(regular_day_choices)
        if not regular_day_choices:
            self.time_to_call.choices = ["Call today"]

        # Third-party callback setup
        thirdparty_upcoming_days = sorted([day for day in self.thirdparty_time_slots.keys() if day != today])
        thirdparty_day_choices = [
            (
                day,
                format_date(
                    datetime.strptime(day, "%Y-%m-%d"),
                    format="EEE d MMM",
                    locale=get_locale(),
                ),
            )
            for day in thirdparty_upcoming_days
        ]

        self.thirdparty_call_another_day.choices.extend(thirdparty_day_choices)
        if not thirdparty_day_choices:
            self.thirdparty_time_to_call.choices = ["Call today"]

    def _setup_selections_for_chosen_days(self):
        """Setup time choices based on previously selected days"""

        # Regular callback
        if self.call_another_day.data:
            self.call_another_time.choices = self.time_slots.get(self.call_another_day.data, [])
        else:
            self.call_another_time.choices.extend(self._get_all_unique_time_slots())

        # Third-party callback
        if self.thirdparty_call_another_day.data:
            self.thirdparty_call_another_time.choices = self.thirdparty_time_slots.get(
                self.thirdparty_call_another_day.data, []
            )
        else:
            self.thirdparty_call_another_time.choices.extend(self._get_all_unique_time_slots(thirdparty_callback=True))

    def _adjust_contact_options_for_availability(self):
        """Remove callback option if no slots are available"""
        if len(self.call_today_time.choices) <= 1 and len(self.call_another_day.choices) <= 1:
            self.contact_type.choices = NO_SLOT_CONTACT_PREFERENCE

    def _get_all_unique_time_slots(self, thirdparty_callback=False):
        """Get all unique time slots sorted by time"""
        all_time_slots = self.time_slots.values() if not thirdparty_callback else self.thirdparty_time_slots.values()
        valid_time_slots = {(time[0], time[1]) for times in all_time_slots for time in times}
        return sorted(valid_time_slots)

    @property
    def time_slots_json(self):
        return json.dumps(self.time_slots)

    @property
    def thirdparty_time_slots_json(self):
        return json.dumps(self.thirdparty_time_slots)

    page_title = _("Contact Civil Legal Advice")

    full_name = StringField(
        _("Your full name"),
        widget=GovTextInput(),
        validators=[
            Length(max=400, message=_("Your full name must be 400 characters or less")),
            InputRequired(message=_("Tell us your name")),
        ],
    )

    contact_type = RadioField(
        _("Select a contact option"),
        widget=ContactRadioInput(is_inline=False, heading_class="govuk-fieldset__legend--m"),
        choices=CONTACT_PREFERENCE,
        validators=[InputRequired(message=_("Tell us how we should get in contact"))],
    )

    contact_number = StringField(
        _("Phone number"),
        widget=GovTextInput(),
        description=_("Enter the full number, including the area code. For example, 01632 960 1111."),
        validators=[
            ValidateIf("contact_type", "callback"),
            InputRequired(message=_("Tell us what number to ring")),
            Length(max=20, message=_("Your telephone number must be 20 characters or less")),
        ],
    )

    time_to_call = RadioField(
        _("Select a time for us to call"),
        widget=ContactRadioInput(is_inline=False, heading_class="govuk-fieldset__legend--s"),
        validators=[
            ValidateIf("contact_type", "callback"),
            InputRequired(message=_("Select a time for us to call")),
        ],
        choices=[_("Call today"), _("Call on another day")],
    )

    call_today_time = SelectField(
        _("Time"),
        choices=[("", "Select a time:")],
        widget=GovSelect(),
        validators=[
            ValidateIf("contact_type", "callback"),
            ValidateIf("time_to_call", "Call today"),
            InputRequired(message=_("Select what time you want to be called today")),
        ],
    )

    call_another_day = SelectField(
        _("Day"),
        choices=[("", "Select a day:")],
        widget=GovSelect(),
        validators=[
            ValidateIf("contact_type", "callback"),
            ValidateIf("time_to_call", "Call on another day"),
            InputRequired(message=_("Select which day you want to be called")),
        ],
    )

    call_another_time = ContactSelectField(
        _("Time"),
        choices=[("", "Select a time:")],
        widget=GovSelect(),
        validators=[
            ValidateIf("contact_type", "callback"),
            ValidateIf("time_to_call", "Call on another day"),
            InputRequired(message=_("Select what time you want to be called")),
            ValidateDayTime(day_field="call_another_day"),
        ],
    )

    announce_call_from_cla = RadioField(
        _("Can we say that we're calling from Civil Legal Advice?"),
        widget=ContactRadioInput(is_inline=False, heading_class="govuk-fieldset__legend--s"),
        choices=[
            (True, _("Yes")),
            (False, _("No - do not say where you are calling from")),
        ],
        validators=[
            ValidateIf("contact_type", "callback"),
            InputRequired(message=_("Select if we can say that we’re calling from Civil Legal Advice")),
        ],
    )

    thirdparty_full_name = StringField(
        _("Full name of the person to call"),
        widget=GovTextInput(),
        validators=[
            ValidateIf("contact_type", "thirdparty"),
            Length(max=400, message=_("Their full name must be 400 characters or less")),
            InputRequired(message=_("Tell us the name of the person to call")),
        ],
    )

    thirdparty_relationship = SelectField(
        _("Relationship to you"),
        choices=THIRDPARTY_RELATIONSHIP_CHOICES,
        widget=GovSelect(),
        validators=[
            ValidateIf("contact_type", "thirdparty"),
            InputRequired(message=_("Tell us how you know this person")),
        ],
    )

    thirdparty_contact_number = StringField(
        _("Phone number"),
        widget=GovTextInput(),
        description=_("Enter the full number, including the area code. For example, 01632 960 1111."),
        validators=[
            ValidateIf("contact_type", "thirdparty"),
            InputRequired(message=_("Tell us what number to ring")),
            Length(max=20, message=_("Your telephone number must be 20 characters or less")),
        ],
    )

    thirdparty_time_to_call = RadioField(
        _("Select a time for us to call"),
        widget=ContactRadioInput(is_inline=False, heading_class="govuk-fieldset__legend--s"),
        validators=[
            ValidateIf("contact_type", "thirdparty"),
            InputRequired(message=_("Select a time for us to call")),
        ],
        choices=[_("Call today"), _("Call on another day")],
    )

    thirdparty_call_today_time = SelectField(
        _("Time"),
        choices=[("", "Select a time:")],
        widget=GovSelect(),
        validators=[
            ValidateIf("contact_type", "thirdparty"),
            ValidateIf(
                "thirdparty_time_to_call",
                "Call today",
            ),
            InputRequired(message=_("Select what time you want to be called today")),
        ],
    )

    thirdparty_call_another_day = SelectField(
        _("Day"),
        choices=[("", "Select a day:")],
        widget=GovSelect(),
        validators=[
            ValidateIf("contact_type", "thirdparty"),
            ValidateIf(
                "thirdparty_time_to_call",
                "Call on another day",
            ),
            InputRequired(message=_("Select which day you want to be called")),
        ],
    )

    thirdparty_call_another_time = SelectField(
        _("Time"),
        choices=[("", "Select a time:")],
        widget=GovSelect(),
        validators=[
            ValidateIf("contact_type", "thirdparty"),
            ValidateIf(
                "thirdparty_time_to_call",
                "Call on another day",
            ),
            InputRequired(message=_("Select what time you want to be called")),
            ValidateDayTime(day_field="thirdparty_call_another_day"),
        ],
    )

    email = StringField(
        _("Email (optional)"),
        widget=GovTextInput(),
        description=_("We will use this to send your reference number."),
        validators=[
            Length(max=255, message=_("Your address must be 255 characters or less")),
            Email(message=_("Invalid email address")),
            Optional(),
        ],
    )

    post_code = StringField(
        _("Postcode (optional)"),
        widget=GovTextInput(),
    )
    address_finder = SelectField(_("Select an address"), choices=[""], widget=GovSelect(), validate_choice=False)
    street_address = TextAreaField(
        _("Street address (optional)"),
        widget=GovTextArea(),
        validators=[
            Length(max=255, message=_("Your address must be 255 characters or less")),
            Optional(),
        ],
    )

    extra_notes = TextAreaField(
        _("Tell us more about your problem (optional)"),
        widget=GovTextArea(),
        validators=[
            Length(max=4000, message=_("Your notes must be 4000 characters or less")),
            Optional(),
        ],
    )

    adaptations = SelectMultipleField(
        _("Do you have any special communication needs? (optional)"),
        widget=ContactCheckboxInput(is_inline=False, heading_class="govuk-fieldset__legend--m"),
        choices=[
            ("bsl_webcam", _("British Sign Language (BSL)")),
            ("text_relay", _("Text relay")),
            ("welsh", _("Welsh")),
            ("is_other_language", _("Other language - need an interpreter")),
            ("other_adaptation", _("Any other communication need")),
        ],
    )
    bsl_email = StringField(
        _("Enter your email address so we can arrange a BSL call"),
        widget=GovTextInput(),
        validators=[
            ValidateIf(
                "email", ""
            ),  # We only care about the bsl_email if the user has not included an email address in the above field.
            ValidateIf("adaptations", "bsl_webcam", condition_type=ValidateIfType.IN),
            Length(max=255, message=_("Your address must be 255 characters or less")),
            Email(message=_("Invalid email address")),
        ],
    )
    other_language = SelectField(
        _("Choose a language"),
        choices=LANG_CHOICES,
        widget=GovSelect(),
        validators=[
            ValidateIf("adaptations", "is_other_language", condition_type=ValidateIfType.IN),
            InputRequired(message=_("Choose a language")),
        ],
    )
    other_adaptation = TextAreaField(
        description=_("Please tell us what you need"),
        widget=GovTextArea(),
        validators=[
            Length(
                max=4000,
                message=_("Your other communication needs must be 4000 characters or fewer"),
            ),
        ],
    )

    submit = SubmitField(_("Submit details"), widget=GovSubmitInput())

    def get_email(self):
        return self.data.get("email") or self.data.get("bsl_email")

    def get_callback_time(self) -> datetime | None:
        """Gets the selected callback time as a datetime"""
        contact_type = self.data.get("contact_type")

        if contact_type not in {"callback", "thirdparty"}:
            return None

        # Determine field prefixes based on contact type
        prefix = "thirdparty_" if contact_type == "thirdparty" else ""

        # Get callback time selection (today or another day)
        time_to_call = self.data.get(f"{prefix}time_to_call")

        if time_to_call == "Call today":
            time_str = self.data.get(f"{prefix}call_today_time")
            return datetime.combine(date=datetime.today(), time=datetime.strptime(time_str, "%H%M").time())
        elif time_to_call == "Call on another day":
            day_str = self.data.get(f"{prefix}call_another_day")
            time_str = self.data.get(f"{prefix}call_another_time")
            return datetime.combine(
                date=datetime.strptime(day_str, "%Y-%m-%d").date(),
                time=datetime.strptime(time_str, "%H%M").time(),
            )

        return None

    def get_payload(self) -> dict:
        """Returns the contact payload."""

        callback_time: datetime = self.get_callback_time()

        requires_action_at: str | None = callback_time.isoformat() if callback_time else None

        safe_to_contact = "SAFE" if self.data.get("contact_type") == "callback" else ""
        payload = {
            "personal_details": {
                "full_name": self.data.get("full_name"),
                "email": self.get_email(),
                "postcode": self.data.get("post_code"),
                "mobile_phone": self.data.get("contact_number"),
                "street": self.data.get("street_address"),
                "safe_to_contact": safe_to_contact,
                "announce_call": True,
            },
            "gtm_anon_id": session.get("gtm_anon_id", None),
            "adaptation_details": {
                "bsl_webcam": "bsl_webcam" in (self.data.get("adaptations", [])),
                "text_relay": "text_relay" in (self.data.get("adaptations", [])),
                "language": "WELSH"
                if "welsh" in (self.data.get("adaptations", []))
                else self.data.get("other_language").upper(),
                "notes": self.data.get("other_adaptation"),
            },
            "client_notes": self.data.get("extra_notes"),
        }
        if self.data.get("contact_type") == "callback":
            payload["requires_action_at"] = requires_action_at
            payload["personal_details"]["announce_call"] = self.data.get("announce_call_from_cla")
            payload["callback_type"] = "web_form_self"

        if self.contact_type.data == "thirdparty":
            payload["thirdparty_details"] = {"personal_details": {}}
            payload["thirdparty_details"]["personal_details"]["full_name"] = self.data.get("thirdparty_full_name")
            payload["thirdparty_details"]["personal_details"]["mobile_phone"] = self.data.get(
                "thirdparty_contact_number"
            )
            payload["thirdparty_details"]["personal_details"]["safe_to_contact"] = "SAFE"
            payload["thirdparty_details"]["personal_relationship"] = self.data.get("thirdparty_relationship").upper()
            payload["callback_type"] = "web_form_third_party"
            payload["requires_action_at"] = requires_action_at

        return payload


class ConfirmationEmailForm(FlaskForm):
    email = StringField(
        _("Receive this confirmation by email"),
        widget=ContactTextInput(
            heading_class="govuk-fieldset__legend--s",
            hint_text=_("We will use this to send your reference number."),
        ),
        validators=[
            Length(max=255, message=_("Your address must be 255 characters or less")),
            Email(message=_("Enter a valid email address")),
            InputRequired(message=_("Tell us what email address to send to")),
        ],
    )
    submit = SubmitField(_("Send"), widget=GovSubmitInput())
