from flask import Blueprint

bp = Blueprint(
    "discrimination",
    __name__,
    template_folder="./templates",
    url_prefix="/discrimination",
)

from app.categories.discrimination import routes  # noqa: E402,F401