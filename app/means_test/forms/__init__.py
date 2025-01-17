from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput
from wtforms.fields.simple import SubmitField
from flask_babel import lazy_gettext as _


class BaseMeansTestForm(FlaskForm):
    title = ""

    submit = SubmitField(_("Continue"), widget=GovSubmitInput())

    def payload(self) -> dict:
        return {}

    @classmethod
    def should_show(cls) -> bool:
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
