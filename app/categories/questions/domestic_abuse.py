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
            destination=CheckDestination.CONTACT,
            category=CheckCategory.DOMESTIC_ABUSE,
            harm_flag=True,
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

    answer_labels = {
        "protect-you-and-your-children": "Help to protect you and your children",
    }

    title = "Domestic Abuse"

    @classmethod
    def valid_choices(cls):
        return ["protect-you-and-your-children"]

    @classmethod
    def get_label(cls, choice: str) -> str:
        """Convert a user answer value to its human-readable label.
            If there is no alternative then will fallback and return the internal value.

        Args:
            choice: The internal choice value (e.g. "asylum")

        Returns:
            The display label (e.g., "Asylum and immigration")
        """
        return dict(cls.answer_labels).get(choice, choice)
