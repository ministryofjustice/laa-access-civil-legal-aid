from flask_wtf import FlaskForm
from wtforms import SelectMultipleField
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput
from wtforms.fields import SubmitField
from app.categories.widgets import CategoryCheckboxInput
from wtforms.validators import InputRequired
from flask_babel import _


class ReasonsForContactingForm(FlaskForm):
    next_step_mapping = {
        "*": "categories.results.contact",
    }

    title = "Why do you want to contact Civil Legal Advice?"

    rfc_choices = SelectMultipleField(
        title,
        widget=CategoryCheckboxInput(hint_text="Select all that apply"),
        validators=[
            InputRequired(message="Select yes if you want to accept functional cookies")
        ],
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

    save = SubmitField("Continue to contact CLA", widget=GovSubmitInput())
