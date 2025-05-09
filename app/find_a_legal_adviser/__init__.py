from flask import Blueprint

bp = Blueprint("find-a-legal-adviser", __name__)

from app.find_a_legal_adviser import routes  # noqa: E402,F401
