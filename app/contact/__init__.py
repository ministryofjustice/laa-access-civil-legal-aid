from flask import Blueprint

bp = Blueprint(
    "contact",
    __name__,
    template_folder="./templates",
)

from app.contact import urls  # noqa: E402,F401
