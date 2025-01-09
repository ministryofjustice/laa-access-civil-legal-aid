from flask_wtf import FlaskForm
from wtforms.fields import SubmitField
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput


class BaseMeansTestForm(FlaskForm):
    submit = SubmitField("Continue", widget=GovSubmitInput())

    @property
    def fields_to_render(self):
        fields = []
        submit_field = None
        for name, field in self._fields.items():
            if isinstance(field, SubmitField):
                submit_field = field
                continue
            else:
                fields.append(field)
        if submit_field:
            fields.append(submit_field)
        return fields

    def payload(self):
        data = self.data
        return {k: v for k, v in data.items() if k not in ["submit", "csrf_token"]}
