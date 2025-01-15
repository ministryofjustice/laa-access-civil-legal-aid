from flask import render_template
from flask_wtf import FlaskForm
from wtforms.fields.simple import SubmitField
from wtforms.validators import InputRequired
from wtforms.widgets import TextInput
from markupsafe import Markup
from wtforms import Field


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
        self.field_with_error = {}

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

    def validate(self, form, extra_validators=None):
        """Validate both inputs"""
        self.errors = []
        self.field_with_error = []
        if not self.value and not self.interval:
            self.errors.append(
                "Enter the total amount of maintenance you receive, or 0 if this doesn’t apply to you"
            )
            self.field_with_error = ["value", "interval"]
            return False
        if not self.value:
            self.errors.append("Amount is required")
            self.field_with_error = ["value"]
            return False
        if not self.interval:
            self.errors.append("Frequency is required")
            self.field_with_error = ["interval"]
            return False
        return True


class ExampleForm(FlaskForm):
    template = "means_test/form-page.html"

    question = CombinedTextField(
        "Test money field", hint_text="Hint text", widget=CombinedTextWidget()
    )

    submit = SubmitField("Continue")
