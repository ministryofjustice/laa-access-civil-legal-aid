from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput
from wtforms.fields.simple import SubmitField
from wtforms.fields.choices import SelectField, SelectMultipleField
from wtforms.csrf.core import CSRFTokenField
from flask_babel import lazy_gettext as _
from flask import session
from app.means_test.fields import MoneyIntervalField, MoneyInterval
import decimal


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

    def summary(self):
        summary = {}
        for field_name, field_instance in self._fields.items():
            if isinstance(field_instance, (SubmitField, CSRFTokenField)):
                continue

            if field_instance.data in [None, "None"]:
                continue

            question = str(field_instance.label.text)
            answer = field_instance.data

            if isinstance(field_instance, SelectField):
                answer = self.get_selected_answers(field_instance)
            if isinstance(field_instance, MoneyIntervalField):
                answer = self.get_money_field_answers(field_instance)
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
    def get_selected_answers(field_instance):
        def choices_filter(choice):
            return field_instance.data and choice[0] in field_instance.data

        answers = list(filter(choices_filter, field_instance.choices))
        answers = [str(answer[1]) for answer in answers]
        if not isinstance(field_instance, SelectMultipleField):
            answers = answers[0]
        return answers

    @staticmethod
    def get_money_field_answers(field_instance):
        if field_instance.data["per_interval_value"] is None:
            return None

        amount = decimal.Decimal(int(field_instance.data["per_interval_value"]) / 100)
        amount = amount.quantize(decimal.Decimal("0.01"))
        interval = MoneyInterval._intervals[field_instance.data["interval_period"]][
            "label"
        ]
        return f"£{amount} {_('every')} {interval}"
