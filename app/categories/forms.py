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

    # Onward page logic, you can route the user to a:
    # - question page using an uninstantiated QuestionForm
    # - internal redirect using an endpoint string
    # - external redirect using a werkzeug.Response
    #
    # Ex: routing_logic = {
    #    "answer_a": QuestionForm
    #    "answer_b": "blueprint.endpoint",
    #    "answer_c": redirect("www.hostname.gov.uk/endpoint")
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
    def get_label(cls, choice: str) -> str:
        """Convert a choice value to its human-readable label.
            If there is no alternative then will fallback and return the internal value.

        Args:
            choice: The internal choice value (e.g. "asylum")

        Returns:
            The display label (e.g., "Asylum and immigration")
        """
        return dict(cls.question.kwargs["choices"]).get(choice, choice)

    @classmethod
    def valid_choices(cls):
        return [choice[0] for choice in cls.question.kwargs["choices"]]

    show_or_divisor = False

    submit = SubmitField(
        "Continue", widget=GovSubmitInput()
    )  # You usually won't need to overwrite this
