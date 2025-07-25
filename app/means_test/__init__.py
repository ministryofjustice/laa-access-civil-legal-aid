from flask import Blueprint

bp = Blueprint("means_test", __name__)
result = Blueprint("result", __name__, url_prefix="/results")
bp.register_blueprint(result)

from app.means_test import urls  # noqa: E402,F401
from app.means_test.constants import EligibilityState  # noqa: E402,F401
