from flask import Blueprint

bp = Blueprint("main", __name__, template_folder="../templates/main")

from app.main import routes  # noqa: E402,F401
from app.main import filters
