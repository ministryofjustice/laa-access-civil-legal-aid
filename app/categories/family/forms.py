from wtforms.fields.choices import RadioField
from wtforms.validators import InputRequired

from app.categories.forms import QuestionForm
from app.categories.constants import FAMILY
from flask_babel import lazy_gettext as _

from app.categories.widgets import CategoryRadioInput


class HaveYouHadFamilyMediationBefore(QuestionForm):
    category = FAMILY

    title = _("Have you taken part in a family mediation session?")

    next_step_mapping = {
        "yes": "categories.results.in_scope",
        "no": {"endpoint": "find-a-legal-adviser.search", "category": "fmed"},
    }

    question = RadioField(
        title,
        widget=CategoryRadioInput(show_divider=False, is_inline=True),
        validators=[
            InputRequired(
                message=_(
                    "Select if you have taken part in a family mediation session before"
                )
            ),
        ],
        choices=[
            ("yes", _("Yes")),
            ("no", _("No")),
        ],
    )
