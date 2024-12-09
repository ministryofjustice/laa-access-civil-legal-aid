from flask import Blueprint
from .domestic_abuse import bp as domestic_abuse_bp
from .discrimination import bp as discrimination_bp
from .asylum_immigration import bp as asylum_immigration_bp
from .housing import bp as housing_bp
from .mental_capacity import bp as mental_capacity_bp
from .community_care import bp as community_care_bp
from .send import bp as send_bp
from .benefits import bp as benefits_bp
from .results import bp as results_bp

bp = Blueprint("categories", __name__)
bp.register_blueprint(domestic_abuse_bp)
bp.register_blueprint(discrimination_bp)
bp.register_blueprint(housing_bp)
bp.register_blueprint(mental_capacity_bp)
bp.register_blueprint(results_bp)
bp.register_blueprint(asylum_immigration_bp)
bp.register_blueprint(community_care_bp)
bp.register_blueprint(send_bp)
bp.register_blueprint(benefits_bp)

from app.categories import urls  # noqa: E402,F401
