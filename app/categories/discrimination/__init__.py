from flask import Blueprint

bp = Blueprint(
    "discrimination",
    __name__,
)

from app.categories.discrimination import urls  # noqa: E402,F401
