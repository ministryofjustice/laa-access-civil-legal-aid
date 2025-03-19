from flask import Blueprint
from flask_babel import lazy_gettext as _

bp = Blueprint("means_test", __name__)

from app.means_test import urls  # noqa: E402,F401
