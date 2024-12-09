from flask import Blueprint

bp = Blueprint(
    "public",
    __name__,
    template_folder="./templates",
)

from app.categories.public import urls  # noqa: E402,F401
