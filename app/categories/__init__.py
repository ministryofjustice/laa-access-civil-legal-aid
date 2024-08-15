from flask import Blueprint

bp = Blueprint("categories", __name__, template_folder="./templates")

from app.categories import routes  # noqa: E402,F401
