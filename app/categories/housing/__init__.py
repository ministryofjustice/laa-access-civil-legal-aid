from flask import Blueprint

bp = Blueprint(
    "housing",
    __name__,
    template_folder="./templates",
    url_prefix="/housing",
)

from app.categories.housing import routes  # noqa: E402,F401
