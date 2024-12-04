from flask import Blueprint

bp = Blueprint(
    "community_care",
    __name__,
    template_folder="./templates",
)

from app.categories.community_care import urls  # noqa: E402,F401
