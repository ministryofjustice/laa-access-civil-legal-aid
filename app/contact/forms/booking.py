from flask_babel import lazy_gettext as _
from app.contact.forms import BaseForm


class BookingForm(BaseForm):
    title = _("Book an appointment with Civil Legal Advice")
