from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput
from wtforms.fields.simple import SubmitField
from flask_babel import gettext as _


class BaseMeansTestForm(FlaskForm):
    title = ""

    submit = SubmitField(_("Continue"), widget=GovSubmitInput())

    def payload(self) -> dict:
        return {}

    @classmethod
    def should_show(cls) -> bool:
        return True
