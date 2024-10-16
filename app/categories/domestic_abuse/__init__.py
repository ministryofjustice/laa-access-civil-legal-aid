from flask import Blueprint

bp = Blueprint(
    "domestic_abuse",
    __name__,
    template_folder="./templates",
    url_prefix="/domestic-abuse",
)

from app.categories.domestic_abuse import routes  # noqa: E402,F401
