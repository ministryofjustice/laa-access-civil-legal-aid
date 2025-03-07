from flask_babel import lazy_gettext as _
from app.means_test.forms import BaseMeansTestForm


class ReviewForm(BaseMeansTestForm):
    title = _("Check your answers and confirm")
