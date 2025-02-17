import json
from flask_wtf import FlaskForm
from flask import request
from wtforms import (
    SelectMultipleField,
    HiddenField,
    StringField,
    RadioField,
    TextAreaField,
    SelectField,
)
from app.config import Config
from govuk_frontend_wtf.wtforms_widgets import (
    GovSubmitInput,
    GovTextInput,
    GovTextArea,
    GovSelect,
)
from app.contact.widgets import (
    ContactRadioInput,
    ContactCheckboxInput,
    ContactSelectMultipleField,
)
from wtforms.fields import SubmitField
from app.categories.widgets import CategoryCheckboxInput
from app.contact.constants import LANG_CHOICES, THIRDPARTY_RELATIONSHIP_CHOICES
from flask_babel import lazy_gettext as _
from wtforms.validators import InputRequired, Length, Optional
from enum import Enum
from app.contact.validators import (
    EmailValidator,
    ValidateIf,
    ValidateIfType,
    ValidateDayTime,
)
from app.api import cla_backend
from datetime import datetime, timedelta
import pytz


class ContactPreference(Enum):
    CALL = ("call", "I will call you")
    CALLBACK = ("callback", "Call me back")
    THIRDPARTY = ("thirdparty", "Call someone else instead of me")

    @classmethod
    def choices(cls):
        return [(choice.value[0], choice.value[1]) for choice in cls]


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
        self.other_language.choices = LANG_CHOICES
        self.thirdparty_relationship.choices = THIRDPARTY_RELATIONSHIP_CHOICES

        self.time_slots = cla_backend.get_time_slots(num_days=8)
        self.thirdparty_time_slots = cla_backend.get_time_slots(
            num_days=8, is_third_party_callback=True
        )
        today = list(self.time_slots)[0]
        self.call_today_time.choices = [("", "Select a day:")] + self.time_slots.get(
            today
        )
        self.thirdparty_call_today_time.choices = [
            ("", "Select a day:")
        ] + self.thirdparty_time_slots.get(today)
        slot_days = list(self.time_slots)[1:8]

        self.call_another_day.choices = [("", "Select a day:")] + [
            (key, datetime.strptime(key, "%Y-%m-%d").strftime("%a %d %b"))
            for key in slot_days
        ]
        self.thirdparty_call_another_day.choices = [("", "Select a day:")] + [
            (key, datetime.strptime(key, "%Y-%m-%d").strftime("%a %d %b"))
            for key in slot_days
        ]
        # If the user has already selected a day field, the time field is populated from that selection
        if self.call_another_day.data:
            if self.call_another_day.data[0]:
                self.call_another_time.choices = [
                    ("", "Select a time:")
                ] + self.time_slots.get(self.call_another_day.data[0])
            else:
                self.call_another_time.choices = [
                    ("", "Select a time:")
                ] + self.get_all_time_slots()
        if self.thirdparty_call_another_day.data:
            if self.thirdparty_call_another_day.data[0]:
                self.thirdparty_call_another_time.choices = [
                    ("", "Select a time:")
                ] + self.thirdparty_time_slots.get(
                    self.thirdparty_call_another_day.data[0]
                )
            else:
                self.thirdparty_call_another_time.choices = [
                    ("", "Select a time:")
                ] + self.get_all_time_slots()

    def get_all_time_slots(self):
        valid_time_slots = set()
        for times in self.time_slots.values():
            for time in times:
                valid_time_slots.add((time[0], time[1]))

        valid_time_slots = list(valid_time_slots)
        sorted_valid_time_slots = sorted(valid_time_slots)

        return sorted_valid_time_slots

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
        widget=ContactRadioInput(),
        choices=ContactPreference.choices(),
        validators=[InputRequired(message=_("Tell us how we should get in contact"))],
    )

    contact_number = StringField(
        _("Phone number"),
        widget=GovTextInput(),
        description=_(
            "Enter the full number, including the area code. For example, 01632 960 1111."
        ),
        validators=[
            ValidateIf("contact_type", "callback", condition_type=ValidateIfType.EQ),
            InputRequired(message=_("Tell us what number to ring")),
            Length(
                max=20, message=_("Your telephone number must be 20 characters or less")
            ),
        ],
    )

    time_to_call = RadioField(
        _("Select a time for us to call"),
        widget=ContactRadioInput(),
        validators=[
            ValidateIf("contact_type", "callback", condition_type=ValidateIfType.EQ),
            InputRequired(message=_("Select a time for us to call")),
        ],
        choices=["Call today", "Call on another day"],
    )

    call_today_time = SelectMultipleField(
        _("Time"),
        choices=[],
        widget=GovSelect(),
        validators=[
            ValidateIf("contact_type", "callback", condition_type=ValidateIfType.EQ),
            ValidateIf("time_to_call", "Call today", condition_type=ValidateIfType.EQ),
            InputRequired(message=_("Select what time you want to be called today")),
        ],
    )

    call_another_day = SelectMultipleField(
        _("Day"),
        choices=[],
        widget=GovSelect(),
        validators=[
            ValidateIf("contact_type", "callback", condition_type=ValidateIfType.EQ),
            ValidateIf(
                "time_to_call", "Call on another day", condition_type=ValidateIfType.EQ
            ),
            InputRequired(message=_("Select which day you want to be called")),
        ],
    )

    call_another_time = ContactSelectMultipleField(
        _("Time"),
        choices=["Select a time:"],
        widget=GovSelect(),
        validators=[
            ValidateIf("contact_type", "callback", condition_type=ValidateIfType.EQ),
            ValidateIf(
                "time_to_call", "Call on another day", condition_type=ValidateIfType.EQ
            ),
            InputRequired(message=_("Select what time you want to be called")),
            ValidateDayTime(day_field="call_another_day"),
        ],
    )

    announce_call_from_cla = RadioField(
        _("Can we say that we're calling from Civil Legal Advice?"),
        widget=ContactRadioInput(),
        choices=[
            (True, _("Yes")),
            (False, _("No - do not say where you are calling from")),
        ],
        validators=[
            ValidateIf("contact_type", "callback", condition_type=ValidateIfType.EQ),
            InputRequired(
                message=_(
                    "Select if we can say that we’re calling from Civil Legal Advice"
                )
            ),
        ],
    )

    thirdparty_full_name = StringField(
        _("Full name of the person to call"),
        widget=GovTextInput(),
        validators=[
            ValidateIf("contact_type", "thirdparty", condition_type=ValidateIfType.EQ),
            Length(
                max=400, message=_("Their full name must be 400 characters or less")
            ),
            InputRequired(message=_("Tell us the name of the person to call")),
        ],
    )

    thirdparty_relationship = SelectMultipleField(
        _("Relationship to you"),
        choices=[],
        widget=GovSelect(),
        validators=[
            ValidateIf("contact_type", "thirdparty", condition_type=ValidateIfType.EQ),
            InputRequired(message=_("Tell us how you know this person")),
        ],
    )

    thirdparty_contact_number = StringField(
        _("Phone number"),
        widget=GovTextInput(),
        description=_(
            "Enter the full number, including the area code. For example, 01632 960 1111."
        ),
        validators=[
            ValidateIf("contact_type", "thirdparty", condition_type=ValidateIfType.EQ),
            InputRequired(message=_("Tell us what number to ring")),
            Length(
                max=20, message=_("Your telephone number must be 20 characters or less")
            ),
        ],
    )

    thirdparty_time_to_call = RadioField(
        _("Select a time for us to call"),
        widget=ContactRadioInput(),
        validators=[
            ValidateIf("contact_type", "thirdparty", condition_type=ValidateIfType.EQ),
            InputRequired(message=_("Select a time for us to call")),
        ],
        choices=["Call today", "Call on another day"],
    )

    thirdparty_call_today_time = SelectMultipleField(
        _("Time"),
        choices=["Select a time:"],
        widget=GovSelect(),
        validators=[
            ValidateIf("contact_type", "thirdparty", condition_type=ValidateIfType.EQ),
            ValidateIf(
                "thirdparty_time_to_call",
                "Call today",
                condition_type=ValidateIfType.EQ,
            ),
            InputRequired(message=_("Select what time you want to be called today")),
        ],
    )

    thirdparty_call_another_day = SelectMultipleField(
        _("Day"),
        choices=[],
        widget=GovSelect(),
        validators=[
            ValidateIf("contact_type", "thirdparty", condition_type=ValidateIfType.EQ),
            ValidateIf(
                "thirdparty_time_to_call",
                "Call on another day",
                condition_type=ValidateIfType.EQ,
            ),
            InputRequired(message=_("Select which day you want to be called")),
        ],
    )

    thirdparty_call_another_time = SelectMultipleField(
        _("Time"),
        choices=[],
        widget=GovSelect(),
        validators=[
            ValidateIf("contact_type", "thirdparty", condition_type=ValidateIfType.EQ),
            ValidateIf(
                "thirdparty_time_to_call",
                "Call on another day",
                condition_type=ValidateIfType.EQ,
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
            EmailValidator(message=_("Invalid email address")),
            Optional(),
        ],
    )

    post_code = StringField(
        _("Postcode (optional)"),
        widget=GovTextInput(),
    )
    address_finder = SelectField(
        _("Select an address"), choices=[""], widget=GovSelect()
    )
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
        widget=ContactCheckboxInput(),
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
            ValidateIf("adaptations", "bsl_webcam", condition_type=ValidateIfType.IN),
            Length(max=255, message=_("Your address must be 255 characters or less")),
            EmailValidator(message=_("Enter your email address")),
        ],
    )
    other_language = SelectMultipleField(
        _("Choose a language"),
        choices=[],
        widget=GovSelect(),
        validators=[
            ValidateIf(
                "adaptations", "is_other_language", condition_type=ValidateIfType.IN
            ),
            InputRequired(message=_("Choose a language")),
        ],
    )
    other_adaptation = TextAreaField(
        _(""),
        description=_(
            "Please tell us what you need"
        ),  # Dywedwch wrthym beth sydd ei angen arnoch
        widget=GovTextArea(),
        validators=[
            Length(
                max=4000,
                message=_(
                    "Your other communication needs must be 4000 characters or fewer"
                ),
            ),
        ],
    )

    submit = SubmitField(_("Submit details"), widget=GovSubmitInput())

    def get_email(self):
        return self.data.get("email") or self.data.get("bsl_email")

    def get_callback_time(self):
        """
        Gets the callback time in both:
        - ISO format (UTC)
        - Readable format (e.g., "Monday, 12 February at 14:30 - 15:00")
        This is used in both the payload and email.

        Returns:
            tuple: (iso_time, formatted_time) or (None, None) if no valid time.
        """
        callback_requested = {"thirdparty", "callback"}
        contact_type = self.data.get("contact_type")

        if contact_type not in callback_requested:
            return None, None

        time_to_call = self.data.get("time_to_call")
        thirdparty_time_to_call = self.data.get("thirdparty_time_to_call")

        def parse_time(time_str, date_str=None):
            """Helper function to parse time with optional date."""
            if not time_str:
                return None
            date = (
                datetime.today().date()
                if not date_str
                else datetime.strptime(date_str, "%Y-%m-%d").date()
            )
            return datetime.strptime(time_str, "%H%M").replace(
                year=date.year, month=date.month, day=date.day
            )

        def format_time(dt):
            """Helper function to format the callback time string."""
            if not dt:
                return None
            end_time = dt + timedelta(minutes=30)
            return dt.strftime("%A, %d %B at %H:%M - ") + end_time.strftime("%H:%M")

        if time_to_call == "Call today":
            time = parse_time(self.data.get("call_today_time", [None])[0])
        elif time_to_call == "Call on another day":
            time = parse_time(
                self.data.get("call_another_time", [None])[0],
                self.data.get("call_another_day", [None])[0],
            )
        elif thirdparty_time_to_call == "Call today":
            time = parse_time(self.data.get("thirdparty_call_today_time", [None])[0])
        elif thirdparty_time_to_call == "Call on another day":
            time = parse_time(
                self.data.get("thirdparty_call_another_time", [None])[0],
                self.data.get("thirdparty_call_another_day", [None])[0],
            )
        else:
            return None, None

        local_tz = pytz.timezone(Config.TIMEZONE)
        iso_time = (
            local_tz.localize(time).astimezone(pytz.utc).isoformat() if time else None
        )

        formatted_time = format_time(time)

        return iso_time, formatted_time

    def get_payload(self) -> dict:
        """
        Returns the contact payload.
        """

        requires_action_at, formatted_time = self.get_callback_time()

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
            "adaptation_details": {
                "bsl_webcam": True
                if "bsl_webcam" in (self.data.get("adaptations") or [])
                else False,
                "text_relay": True
                if "text_relay" in (self.data.get("adaptations") or [])
                else False,
                "language": "WELSH"
                if "welsh" in (self.data.get("adaptations") or [])
                else self.data.get("other_language")[0].upper(),
                "notes": self.data.get("other_adaptation"),
            },
        }
        if self.data.get("contact_type") == "callback":
            payload["requires_action_at"] = requires_action_at
            payload["personal_details"]["announce_call"] = self.data.get(
                "announce_call_from_cla"
            )
            payload["callback_type"] = "web_form_self"

        if self.contact_type.data == "thirdparty":
            payload["thirdparty_details"] = {"personal_details": {}}
            payload["thirdparty_details"]["personal_details"]["full_name"] = (
                self.data.get("thirdparty_full_name")
            )
            payload["thirdparty_details"]["personal_details"]["mobile_phone"] = (
                self.data.get("thirdparty_contact_number")
            )
            payload["thirdparty_details"]["personal_details"]["safe_to_contact"] = (
                "SAFE"
            )
            payload["thirdparty_details"]["personal_relationship"] = self.data.get(
                "thirdparty_relationship"
            )[0].upper()
            payload["callback_type"] = "web_form_third_party"
            payload["requires_action_at"] = requires_action_at

        return payload
