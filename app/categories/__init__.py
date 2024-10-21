from flask import Blueprint
from .domestic_abuse import bp as domestic_abuse_bp
from .discrimination import bp as discrimination_bp

bp = Blueprint("categories", __name__, template_folder="templates")
bp.register_blueprint(domestic_abuse_bp)
bp.register_blueprint(discrimination_bp)

from app.categories import routes  # noqa: E402,F401
