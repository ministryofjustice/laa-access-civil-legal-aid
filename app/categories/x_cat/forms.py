from wtforms.fields.choices import RadioField
from wtforms.validators import InputRequired
from app.categories.forms import QuestionForm
from app.categories.widgets import CategoryRadioInput
from flask_babel import lazy_gettext as _
from app.categories.constants import Category


class AreYouUnder18Form(QuestionForm):
    title = _("Are you under 18?")

    next_step_mapping = {
        "yes": "contact.contact_us",
        "no": "categories.results.in_scope",
    }

    question = RadioField(
        title,
        widget=CategoryRadioInput(show_divider=False, is_inline=True),
        validators=[InputRequired(message=_("Select if you’re under 18"))],
        choices=[
            ("yes", _("Yes")),
            ("no", _("No")),
        ],
    )


class AntiSocialBehaviourForm(QuestionForm):
    title = _("Were you accused by a landlord or the council?")
    category = Category(
        _("Anti-social behaviour and gangs"), "ANTI_SOCIAL_BEHAVIOUR", None, None
    )
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
