from flask import render_template
from wtforms.fields.simple import SubmitField
from wtforms.validators import InputRequired
from wtforms.widgets import TextInput
from markupsafe import Markup
from wtforms import Field
from app.means_test.forms import BaseMeansTestForm
from app.means_test.validators import MoneyIntervalAmountRequired, ValidateIfSession
from flask_babel import lazy_gettext as _


class CombinedTextWidget(TextInput):
    def __call__(self, field, *args, **kwargs):
        # Pass the current values to the template
        return Markup(
            render_template(
                "means_test/components/money-field.html",
                field=field,
                value=field.value,
                interval=field.interval,
            )
        )


class CombinedTextField(Field):
    """
    A field that handles two separate text inputs.
    The raw data will contain both values separately.
    """

    validators = [InputRequired("Test")]

    def __init__(self, label=None, hint_text=None, validators=None, **kwargs):
        super().__init__(label, validators, **kwargs)
        self.title = label
        self.hint = hint_text
        self.value = None  # Amount
        self.interval = None  # Frequency
        self.field_with_error = []

    def process_formdata(self, valuelist):
        """Process the form data from both inputs"""
        if valuelist and len(valuelist) >= 2:
            # Handle the data coming from the form fields named field.id[value] and field.id[interval]
            self.value = valuelist[0]
            self.interval = valuelist[1]

    def _value(self):
        if self.raw_data:
            return " ".join(self.raw_data)
        else:
            return self.data and self.data.strftime(self.format) or ""

    # def validate(self, form, extra_validators=None):
    #     """Validate both inputs"""
    #     self.errors = []
    #     self.field_with_error = []
    #     if not self.value and not self.interval:
    #         self.errors.append(
    #             "Enter the total amount of maintenance you receive, or 0 if this doesn’t apply to you"
    #         )
    #         self.field_with_error = ["value", "interval"]
    #         return False
    #     if not self.value:
    #         self.errors.append("Amount is required")
    #         self.field_with_error = ["value"]
    #         return False
    #     if not self.interval:
    #         self.errors.append("Frequency is required")
    #         self.field_with_error = ["interval"]
    #         return False
    #     return True


class ExampleForm(BaseMeansTestForm):
    template = "means_test/form-page.html"

    question = CombinedTextField(
        "Test money field",
        hint_text="Hint text",
        widget=CombinedTextWidget(),
        validators=[
            MoneyIntervalAmountRequired(
                message=_(
                    "Enter the Working Tax Credit you receive, or 0 if this doesn’t apply to you"
                ),
                freq_message=_("Tell us how often you receive Working Tax Credit"),
                amount_message=_(
                    "Tell us how much Working Tax Credit you receive"
                ),  # this is followed by the time period, e.g. "... each week"
            )
        ],
    )

    partner_question = CombinedTextField(
        "Test money field",
        hint_text="Hint text",
        widget=CombinedTextWidget(),
        validators=[
            ValidateIfSession("has_partner", True),
            MoneyIntervalAmountRequired(
                message=_(
                    "Enter the Working Tax Credit your partner receives, or 0 if it doesn’t apply"
                ),
                freq_message=_(
                    "Tell us how often your partner receives Working Tax Credit"
                ),
                amount_message=_(
                    "Tell us how much Working Tax Credit your partner receives"
                ),  # this is followed by the time period, e.g. "... each week"
            ),
        ],
    )

    submit = SubmitField("Continue")
