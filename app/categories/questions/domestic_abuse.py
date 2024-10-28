from app.categories.forms import QuestionForm
from wtforms import RadioField

from app.categories.redirect import CheckRedirect, CheckDestination, CheckCategory
from app.categories.widgets import CategoryRadioInput
from wtforms.validators import InputRequired


class AreYouAtRiskOfHarmForm(QuestionForm):
    category = "Domestic Abuse"

    title = "Are you or your children at immediate risk of harm?"

    routing_logic = {
        "yes": CheckRedirect(
            destination=CheckDestination.CONTACT, category=CheckCategory.DOMESTIC_ABUSE
        ),
        "no": CheckRedirect(
            destination=CheckDestination.MEANS_TEST,
            category=CheckCategory.DOMESTIC_ABUSE,
        ),
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
    routing_logic = {"protect-you-and-your-children": AreYouAtRiskOfHarmForm}

    title = "Domestic Abuse"

    @classmethod
    def valid_choices(cls):
        return ["protect-you-and-your-children"]
