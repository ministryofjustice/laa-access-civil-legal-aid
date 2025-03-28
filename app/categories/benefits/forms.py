from wtforms import RadioField
from wtforms.validators import InputRequired
from flask_babel import lazy_gettext as _
from app.categories.widgets import CategoryRadioInput
from app.categories.forms import QuestionForm
from app.categories.constants import BENEFITS


FALA_REDIRECT = {
    "endpoint": "find-a-legal-adviser.search",
    "category": "wb",
}


class AppealQuestionForm(QuestionForm):
    category = BENEFITS
    title = _("Where will the appeal be held?")
    next_step_mapping = {
        "supreme_court": FALA_REDIRECT,
        "upper_tribunal": FALA_REDIRECT,
        "appeal_court": FALA_REDIRECT,
        "none": "categories.benefits.cannot_find_your_problem",
    }
    question = RadioField(
        title,
        widget=CategoryRadioInput(show_divider=True, label_class="govuk-body", is_page_heading=False),
        validators=[InputRequired(message=_("Select where the appeal will be held"))],
        choices=[
            ("upper_tribunal", _("Upper Tribunal (Administrative Appeals Chamber)")),
            ("supreme_court", _("Supreme Court")),
            ("appeal_court", _("Court of Appeal")),
            ("", ""),
            ("none", _("None of these")),
        ],
    )
