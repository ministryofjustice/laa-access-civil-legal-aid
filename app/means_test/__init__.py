from flask import Blueprint
from flask_babel import lazy_gettext as _

bp = Blueprint("means_test", __name__)
result = Blueprint("result", __name__, url_prefix="/results")
bp.register_blueprint(result)

YES = "1"
YES_LABEL = _("Yes")
NO = "0"
NO_LABEL = _("No")


def is_yes(value):
    return YES == value


from app.means_test import urls  # noqa: E402,F401
