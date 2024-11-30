from flask import Blueprint
from .domestic_abuse import bp as domestic_abuse_bp
from .discrimination import bp as discrimination_bp
from .family import bp as family_bp

bp = Blueprint("categories", __name__)
bp.register_blueprint(domestic_abuse_bp)
bp.register_blueprint(discrimination_bp)
bp.register_blueprint(family_bp)

from app.categories import routes  # noqa: E402,F401
