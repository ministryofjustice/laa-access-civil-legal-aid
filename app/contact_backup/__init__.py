from flask import Blueprint

bp = Blueprint(
    "contact_backup",
    __name__,
    template_folder="./templates",
)

from app.contact_backup import urls  # noqa: E402,F401
