from wtforms import SubmitField, RadioField, Form
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput
from app.categories.widgets import CategoryRadioInput
from wtforms.validators import InputRequired


class QuestionForm(Form):
    """Base form for question pages with configurable routing based on answers."""

    category = "Question category"  # Populates the H1, subclasses should overwrite this with their category of law

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
        validators=[InputRequired(message="Validation failed message")],
        choices=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
    )

    submit = SubmitField("Continue", widget=GovSubmitInput())
