from flask import Blueprint

bp = Blueprint(
    "domestic_abuse",
    __name__,
    template_folder="./templates",
)

from app.categories.domestic_abuse import urls  # noqa: E402,F401
