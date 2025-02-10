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
from govuk_frontend_wtf.wtforms_widgets import (
    GovSubmitInput,
    GovTextInput,
    GovTextArea,
    GovSelect,
)
from app.contact.widgets import ContactRadioInput, ContactCheckboxInput
from wtforms.fields import SubmitField
from app.categories.widgets import CategoryCheckboxInput
from app.contact.constants import LANG_CHOICES
from flask_babel import lazy_gettext as _
from wtforms.validators import InputRequired, Length, Optional
from enum import Enum
from app.contact.validators import EmailValidator, ValidateIf, ValidateIfType
from app.find_a_legal_adviser.validators import ValidRegionPostcode


class ContactPreference(Enum):
    CALL = ("call", "I will call you")
    CALLBACK = ("callback", "Call me back")
    THIRDPARTY = ("thirdparty", "Call someone else instead of me")

    @classmethod
    def choices(cls):
        return [(choice.value[0], choice.value[1]) for choice in cls]


class ReasonsForContactingForm(FlaskForm):
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
        validators=[
            Length(max=12, message=_("Your postcode must be 12 characters or less")),
            ValidRegionPostcode(),
            Optional(),
        ],
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
        choices=(LANG_CHOICES),
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
