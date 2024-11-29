from flask import Blueprint
from .domestic_abuse import bp as domestic_abuse_bp
from .discrimination import bp as discrimination_bp
from .housing import bp as housing_bp

bp = Blueprint("categories", __name__)
bp.register_blueprint(domestic_abuse_bp)
bp.register_blueprint(discrimination_bp)
bp.register_blueprint(housing_bp)

from app.categories import urls  # noqa: E402,F401
