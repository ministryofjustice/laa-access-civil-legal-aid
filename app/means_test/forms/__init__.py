from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput
from wtforms.fields.simple import SubmitField
from wtforms.fields.choices import SelectField, SelectMultipleField
from wtforms.csrf.core import CSRFTokenField
from flask_babel import lazy_gettext as _
from flask import session
from app.means_test.fields import (
    MoneyIntervalField,
    MoneyInterval,
    MoneyField,
    YesNoField,
)
import decimal
from wtforms.fields.core import Field
from app.means_test.validators import ValidateIf, StopValidation, ValidateIfSession


class BaseMeansTestForm(FlaskForm):
    @property
    def page_title(self):
        if self.partner_title != "" and session.get_eligibility().has_partner:
            return self.partner_title
        return self.title

    title = ""

    partner_title = ""

    template = "means_test/form-page.html"

    submit = SubmitField(_("Continue"), widget=GovSubmitInput())

    def payload(self) -> dict:
        return {}

    @classmethod
    def should_show(cls) -> bool:
        """
        Controls whether the form page should be shown or skipped during the Means Test, for example
        if the user selects they receive no benefits then the benefits page should be skipped as follows:

        return session.get_eligibility().forms.get("about-you", {}).get("on_benefits") == YES
        """
        return True

    def render_conditional(self, field, sub_field, conditional_value) -> str:
        """
        Make field conditional using govuk-frontend conditional logic

        :param field: The controlling field
        :param sub_field: The controlled field
        :param conditional_value: The value the controlling field should have to show the controlled field
        :return str: The render field and subfield:
        """

        sub_field_rendered = sub_field()
        conditional = {"value": conditional_value, "html": sub_field_rendered}
        field.render_kw = {"conditional": conditional}
        return field()

    def filter_summary(self, summary: dict) -> dict:
        """Override this method to remove items from review page for this given form"""
        return summary

    def is_unvalidated_conditional_field(self, field: Field):
        # Return True if field has a ValidateIf or ValidateIfSession validator that raise a StopValidation
        for validator in field.validators:
            if isinstance(validator, (ValidateIf, ValidateIfSession)):
                try:
                    validator(self, field)
                except StopValidation:
                    return True
                except Exception:
                    return False
        return False

    def summary(self) -> dict:
        """
        Generates a summary of all fields in this form, including their labels (questions) and formatted values (answers).
        Monetary fields will have a '£' prefix, and selection fields will display their choice label.

        Fields with no data or empty values will be excluded.

        :return: A dictionary summarizing the form fields.
        Each entry follows this structure:
        {
            "question": field label,
            "answer": formatted field value (or choice label for selection fields),
            "id": field ID
        }
        """
        summary = {}
        for field_name, field_instance in self._fields.items():
            if isinstance(field_instance, (SubmitField, CSRFTokenField)):
                continue

            if field_instance.data in [None, "None"]:
                continue

            # Skip fields that use ValidateIf or ValidateIfSession validator that raise a StopValidation
            if self.is_unvalidated_conditional_field(field_instance):
                continue

            question = str(field_instance.label.text)
            answer = field_instance.data

            if isinstance(field_instance, YesNoField):
                answer = field_instance.value
            elif isinstance(field_instance, SelectField):
                answer = self.get_selected_answer(field_instance)
            elif isinstance(field_instance, MoneyIntervalField):
                answer = self.get_money_interval_field_answers(field_instance)
            elif isinstance(field_instance, MoneyField):
                answer = self.get_money_field_answers(field_instance)

            # Skip empty answers
            if answer is None:
                continue

            summary[field_instance.name] = {
                "question": question,
                "answer": answer,
                "id": field_instance.id,
            }

        summary = self.filter_summary(summary)
        return summary

    @staticmethod
    def get_selected_answer(field_instance):
        def selected_answers_only(choice):
            return field_instance.data and choice[0] in field_instance.data

        # Remove any unselected choices
        selected_choices = list(filter(selected_answers_only, field_instance.choices))
        # Get the labels of the selected answers
        answer_labels = [str(choice[1]) for choice in selected_choices]
        if not isinstance(field_instance, SelectMultipleField):
            return answer_labels[0]
        return answer_labels

    @staticmethod
    def get_money_interval_field_answers(field_instance):
        # Handle the property interval dictionary
        if isinstance(field_instance, dict):
            if field_instance.get("per_interval_value") is None:
                return None
            if field_instance.get("per_interval_value") == 0:
                return "£0"
            per_interval = field_instance.get("per_interval_value")
            interval_period = field_instance.get("interval_period")
        else:
            per_interval = field_instance.data["per_interval_value"]
            interval_period = field_instance.data["interval_period"]

            if field_instance.data["per_interval_value"] is None:
                return None

            if field_instance.data["per_interval_value"] == 0:
                return "£0"

        amount = decimal.Decimal(int(per_interval) / 100)
        amount = amount.quantize(decimal.Decimal("0.01"))
        interval = MoneyInterval._intervals[interval_period]["label"]
        return f"£{amount} ({interval})"

    @staticmethod
    def get_money_field_answers(field_instance):
        if isinstance(field_instance, int):
            if field_instance == 0:
                return "£0"
            return f"£{field_instance / 100:.2f}"
        if field_instance.data == 0:
            return "£0"

        return f"£{field_instance._value()}"
