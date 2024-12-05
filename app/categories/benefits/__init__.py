from flask import Blueprint

bp = Blueprint(
    "benefits",
    __name__,
)

from app.categories.benefits import urls  # noqa: E402,F401
