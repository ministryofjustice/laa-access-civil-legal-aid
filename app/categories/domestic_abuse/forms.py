from app.categories.forms import QuestionForm
from wtforms import RadioField
from app.categories.widgets import CategoryRadioInput
from wtforms.validators import InputRequired


class AreYouAtRiskOfHarmForm(QuestionForm):
    category = "Domestic Abuse"

    title = "Are you or your children at immediate risk of harm?"

    question = RadioField(
        title,
        widget=CategoryRadioInput(),
        validators=[
            InputRequired(message="Select if you are at immediate risk of harm?")
        ],
        choices=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
    )
