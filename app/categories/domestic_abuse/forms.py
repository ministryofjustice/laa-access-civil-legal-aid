from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovRadioInput, GovSubmitInput
from wtforms import RadioField, SubmitField
from wtforms.validators import InputRequired


class AreYouAtRiskOfHarmForm(FlaskForm):
    category = "Discrimination"

    title = "Are you at immediate risk of harm?"

    question = RadioField(
        "",
        widget=GovRadioInput(),
        validators=[
            InputRequired(message="Select if you are at immediate risk of harm?")
        ],
        choices=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
    )

    submit = SubmitField("Continue", widget=GovSubmitInput())
