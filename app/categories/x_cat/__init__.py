from flask import Blueprint

bp = Blueprint(
    "x_cat",
    __name__,
    template_folder="./templates",
)

from app.categories.x_cat import urls  # noqa: E402,F401
