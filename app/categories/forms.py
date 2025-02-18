from wtforms import SubmitField, RadioField, Form
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput
from app.categories.widgets import CategoryRadioInput
from wtforms.validators import InputRequired
from flask_babel import gettext as _
from app.categories.constants import Category


class QuestionForm(Form):
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
        "yes": "categories.results.in_scope",
        "no": "categories.results.in_scope",
    }

    question = RadioField(
        title,
        description=_("This could be you, a child or someone else."),
        widget=CategoryRadioInput(show_divider=False, is_inline=True),
        validators=[
            InputRequired(message=_("Select if you’re worried about someone’s safety"))
        ],
        choices=[
            ("yes", _("Yes")),
            ("no", _("No")),
        ],
    )


class ChildInCareQuestionForm(QuestionForm):
    category = "Question category"

    title = _("Is this about a child who is or has been in care?")

    next_step_mapping = {
        "yes": "contact.contact_us",
        "no": "categories.results.in_scope",
    }

    question = RadioField(
        title,
        widget=CategoryRadioInput(show_divider=False, is_inline=True),
        validators=[
            InputRequired(message=_("Select if the child is or has been in care"))
        ],
        choices=[
            ("yes", _("Yes")),
            ("no", _("No")),
        ],
    )
