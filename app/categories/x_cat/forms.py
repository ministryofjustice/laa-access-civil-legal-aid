from wtforms.fields.choices import RadioField
from wtforms.validators import InputRequired
from app.categories.forms import QuestionForm
from app.categories.widgets import CategoryRadioInput
from flask_babel import lazy_gettext as _


class AreYouUnder18Form(QuestionForm):
    title = _("Are you under 18?")

    next_step_mapping = {
        "yes": "categories.results.contact",
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
