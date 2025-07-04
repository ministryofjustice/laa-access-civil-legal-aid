from wtforms import SubmitField, RadioField
from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput
from app.categories.widgets import CategoryRadioInput
from wtforms.validators import InputRequired
from flask_babel import lazy_gettext as _
from app.categories.constants import Category


class QuestionForm(FlaskForm):
    """Base form for question pages with configurable routing based on answers."""

    # Populates the H1, subclasses should overwrite this with their category of law
    category: Category

    title = "Question title"  # Populates the H2 and page title, subclasses overwrite this with their question title

    # Onward page logic, subclasses should overwrite this with their own mapping
    # This routes the user to the given endpoint based on their answer
    next_step_mapping = {
        "yes": "categories.results.in_scope",
        "no": "categories.out_of_scope",
    }

    question = RadioField(
        title,  #  The question title should be the label of the form
        widget=CategoryRadioInput(
            show_divider=False
        ),  # Uses our override class to support setting custom CSS on the label title
        validators=[InputRequired(message=_("Validation failed message"))],
        choices=[
            ("yes", _("Yes")),
            ("no", _("No")),
        ],
    )

    submit = SubmitField(_("Continue"), widget=GovSubmitInput())

    def __init__(self, *args, **kwargs):
        if "category" in kwargs:
            self.category = kwargs.pop("category")
        super().__init__(*args, **kwargs)


class SafeguardingQuestionForm(QuestionForm):
    category = "Question category"

    title = _("Are you worried about someone's safety?")

    next_step_mapping = {
        "yes": {"endpoint": "contact.contact_us_fast_tracked", "reason": "harm"},
        "no": {"endpoint": "contact.contact_us_fast_tracked", "reason": "other"},
    }

    question = RadioField(
        title,
        description=_("This could be you, a child or someone else."),
        widget=CategoryRadioInput(show_divider=False, is_inline=True),
        validators=[InputRequired(message=_("Select if you’re worried about someone’s safety"))],
        choices=[
            ("yes", _("Yes")),
            ("no", _("No")),
        ],
    )


class ChildInCareQuestionForm(QuestionForm):
    category = "Question category"

    title = _("Is this about a child who is or has been in care?")

    next_step_mapping = {
        "yes": {"endpoint": "contact.contact_us_fast_tracked", "reason": "other"},
        "no": "categories.results.in_scope",
    }

    question = RadioField(
        title,
        widget=CategoryRadioInput(show_divider=False, is_inline=True),
        validators=[InputRequired(message=_("Select if the child is or has been in care"))],
        choices=[
            ("yes", _("Yes")),
            ("no", _("No")),
        ],
    )


class PreviousFamilyMediationQuestionForm(QuestionForm):
    category = "Question category"

    title = _("Have you taken part in a family mediation session?")

    next_step_mapping = {
        "yes": "categories.results.in_scope",
        "no": {"endpoint": "find-a-legal-adviser.search", "category": "fmed"},
    }

    question = RadioField(
        title,
        widget=CategoryRadioInput(show_divider=False, is_inline=True),
        validators=[InputRequired(message=_("Select if you have taken part in a family mediation session"))],
        choices=[
            ("yes", _("Yes")),
            ("no", _("No")),
        ],
    )
