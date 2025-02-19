from flask import Blueprint

bp = Blueprint(
    "housing",
    __name__,
    template_folder="./templates",
)

from app.categories.housing import urls  # noqa: E402,F401
