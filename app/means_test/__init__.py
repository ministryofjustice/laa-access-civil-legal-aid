from flask import Blueprint

bp = Blueprint("means_test", __name__)
result = Blueprint("result", __name__, url_prefix="/results")
bp.register_blueprint(result)

YES = "1"
NO = "0"


def is_yes(value):
    return YES == value


from app.means_test import urls  # noqa: E402,F401
