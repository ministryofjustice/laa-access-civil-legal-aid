from flask import Blueprint

YES = "1"
NO = "0"

bp = Blueprint(
    "contact",
    __name__,
    template_folder="./templates",
)

from app.contact import urls  # noqa: E402,F401
