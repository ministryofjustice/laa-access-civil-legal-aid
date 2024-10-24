from wtforms import SubmitField, RadioField, Form
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput
from app.categories.widgets import CategoryRadioInput
from wtforms.validators import InputRequired


class QuestionForm(Form):
    """Base FlaskForm for populating a single question page,
    passing a child of this to the question-page.html template will populate a question page.

    This base class has an example implementation you should overwrite to create new question forms.
    """

    category = "Question category"  # Populates the H1, subclasses should overwrite this with their category of law

    # Populates the H2 and page title, subclasses overwrite this with their question title
    title = "Question title"

    # Onward page logic, to route the user to a question map a valid choice to a question
    # to route the user to an onward page provide an HTTP Response routing the user onwards
    # Ex: next_question = {
    #    "Yes": QuestionForm
    #    "No": view function as a string
    # }
    routing_logic = {}

    question = RadioField(
        title,  #  The question title should be the label of the form
        widget=CategoryRadioInput(),  # Uses our override class to support setting custom CSS on the label title
        validators=[InputRequired(message="Validation failed message")],
        choices=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
    )

    @classmethod
    def valid_choices(cls):
        return [choice[0] for choice in cls.question.kwargs["choices"]]

    show_or_divisor = False

    submit = SubmitField(
        "Continue", widget=GovSubmitInput()
    )  # You usually won't need to overwrite this
