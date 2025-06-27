from flask_wtf import FlaskForm
from wtforms.fields.simple import SubmitField
from flask_babel import lazy_gettext as _
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput


class BaseForm(FlaskForm):
    title = ""
    template = "contact/form-page.html"

    submit = SubmitField(_("Continue"), widget=GovSubmitInput())

    @classmethod
    def should_show(cls) -> bool:
        """
        Controls whether the form page should be shown or skipped during the contact journey.
        """
        return True
