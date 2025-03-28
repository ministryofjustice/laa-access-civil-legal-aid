from flask_babel import lazy_gettext as _
from wtforms import RadioField
from wtforms.validators import InputRequired
from app.categories.widgets import CategoryRadioInput
from app.categories.forms import QuestionForm
from app.categories.constants import PUBLIC_LAW


class PolicePrisonOrDetentionCentreForm(QuestionForm):
    title = _("Is this to do with police, prisons or detention centres?")
    category = PUBLIC_LAW
    next_step_mapping = {
        "yes": {
            "endpoint": "find-a-legal-adviser.search",
            "category": "aap",
        },
        "no": {
            "endpoint": "find-a-legal-adviser.search",
            "category": "pub",
        },
    }

    question = RadioField(
        title,
        widget=CategoryRadioInput(show_divider=False, is_inline=True),
        validators=[InputRequired(message=_("Select if this is about the police, prisons or detention centres"))],
        choices=[
            ("yes", _("Yes")),
            ("no", _("No")),
        ],
    )
