from flask import Blueprint

bp = Blueprint(
    "family",
    __name__,
    template_folder="./templates",
    url_prefix="/family",
)

from app.categories.family import routes  # noqa: E402,F401
