from flask import Blueprint

bp = Blueprint("means_test", __name__)

YES = "1"
NO = "0"


def is_yes(value):
    return YES == value


from app.means_test import urls  # noqa: E402,F401
