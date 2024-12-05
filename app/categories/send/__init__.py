from flask import Blueprint

bp = Blueprint(
    "send",
    __name__,
    template_folder="./templates",
)

from app.categories.send import urls  # noqa: E402,F401
