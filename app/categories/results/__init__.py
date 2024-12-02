from flask import Blueprint

bp = Blueprint(
    "results",
    __name__,
    template_folder="./templates",
)

from app.categories.results import urls  # noqa: E402,F401
