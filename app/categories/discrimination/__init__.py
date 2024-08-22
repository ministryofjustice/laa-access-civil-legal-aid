from flask import Blueprint

bp = Blueprint("discrimination", __name__, template_folder="./templates")

from app.categories.discrimination import routes  # noqa: E402,F401
