from flask import Blueprint

bp = Blueprint(
    "family",
    __name__,
    template_folder="./templates",
)

from app.categories.family import urls  # noqa: E402,F401
