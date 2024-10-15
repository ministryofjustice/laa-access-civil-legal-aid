from flask import Blueprint
from .domestic_abuse import bp as domestic_abuse_bp

bp = Blueprint("categories", __name__, template_folder="templates")
bp.register_blueprint(domestic_abuse_bp)

from app.categories import routes  # noqa: E402,F401

__all__ = ["bp"]
