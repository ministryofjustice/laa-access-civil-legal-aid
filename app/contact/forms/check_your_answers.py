from flask_babel import lazy_gettext as _
from app.contact.forms import BaseForm


class CheckYourAnswers(BaseForm):
    title = _("Check your answers")
    url = "check-your-answers"
    template = "contact/check-your-answers.html"
