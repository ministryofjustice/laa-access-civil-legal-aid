from flask import Blueprint

bp = Blueprint(
    "more_problems",
    __name__,
    template_folder="./templates",
)

from app.categories.more_problems import urls  # noqa: E402,F401
