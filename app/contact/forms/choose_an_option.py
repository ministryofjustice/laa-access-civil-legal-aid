from flask_babel import lazy_gettext as _
from app.contact.forms import BaseForm


class OptionForm(BaseForm):
    title = _("Choose an option for your appointment")
