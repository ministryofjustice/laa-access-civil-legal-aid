from flask import Blueprint

bp = Blueprint(
    "asylum_immigration",
    __name__,
    template_folder="./templates",
)

from app.categories.asylum_immigration import urls  # noqa: E402,F401
