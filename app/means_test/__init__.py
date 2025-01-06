from flask import Blueprint

bp = Blueprint("means_test", __name__)

from app.means_test import routes  # noqa: E402,F401
