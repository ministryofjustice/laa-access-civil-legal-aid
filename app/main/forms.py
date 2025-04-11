from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovRadioInput, GovSubmitInput
from wtforms.fields import RadioField, SubmitField
from wtforms.validators import InputRequired
from flask_babel import lazy_gettext as _


class CookiesForm(FlaskForm):
    functional = RadioField(
        _("Can we use functional cookies?"),
        widget=GovRadioInput(),
        validators=[
            InputRequired(
                message=_("Select yes if you want to accept functional cookies")
            )
        ],
        choices=[("no", _("No")), ("yes", _("Yes"))],
        default="no",
    )
    analytics = RadioField(
        _("Can we use analytics cookies?"),
        widget=GovRadioInput(),
        validators=[
            InputRequired(
                message=_("Select yes if you want to accept analytics cookies")
            )
        ],
        choices=[("no", _("No")), ("yes", _("Yes"))],
        default="no",
    )
    save = SubmitField(_("Save cookie settings"), widget=GovSubmitInput())
