from flask_wtf import FlaskForm
from wtforms.fields import SubmitField
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput


class BaseMeansTestForm(FlaskForm):
    submit = SubmitField("Continue", widget=GovSubmitInput())

    def payload(self):
        data = self.data
        return {k: v for k, v in data.items() if k not in ["submit", "csrf_token"]}
