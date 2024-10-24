from app.categories.forms import QuestionForm
from wtforms import RadioField
from app.categories.widgets import CategoryRadioInput
from wtforms.validators import InputRequired
from flask import redirect


class AreYouAtRiskOfHarmForm(QuestionForm):
    category = "Domestic Abuse"

    title = "Are you or your children at immediate risk of harm?"

    routing_logic = {
        "yes": redirect("https://checklegalaid.service.gov.uk/domestic_abuse_contact"),
        "no": "categories.index",
    }

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


class DomesticAbuseTraversal(QuestionForm):
    routing_logic = {
        "protect-you-and-your-children": AreYouAtRiskOfHarmForm,
        "default": AreYouAtRiskOfHarmForm,
    }

    title = "Domestic Abuse"

    @classmethod
    def valid_choices(cls):
        return ["protect-you-and-your-children"]
