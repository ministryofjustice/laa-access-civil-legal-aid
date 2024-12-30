from wtforms import RadioField
from wtforms.validators import InputRequired
from app.categories.widgets import CategoryRadioInput
from app.categories.forms import QuestionForm
from flask_babel import lazy_gettext as _


class AntiSocialBehaviourForm(QuestionForm):
    title = _("Were you accused by a landlord or the council?")
    category = "Anti-social behaviour and gangs"
    next_step_mapping = {
        "yes": {
            "endpoint": "categories.results.in_scope",
        },
        "no": {
            "endpoint": "find-a-legal-adviser.search",
        },
    }

    question = RadioField(
        title,
        widget=CategoryRadioInput(show_divider=False, is_inline=True),
        validators=[
            InputRequired(
                message=_(
                    "Select ‘Yes’ if you were accused by a landlord or the council"
                )
            )
        ],
        choices=[
            ("yes", _("Yes")),
            ("no", _("No")),
        ],
    )
