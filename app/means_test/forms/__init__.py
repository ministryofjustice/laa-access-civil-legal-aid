from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput
from wtforms.fields.simple import SubmitField
from flask_babel import lazy_gettext as _
from flask import session


class BaseMeansTestForm(FlaskForm):
    @property
    def page_title(self):
        if self.partner_title != "" and session.get_eligibility().has_partner:
            return self.partner_title
        return self.title

    title = ""

    partner_title = ""

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
