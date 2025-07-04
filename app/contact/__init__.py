from flask import Blueprint

bp = Blueprint("contact_us", __name__)

from app.contact import urls  # noqa: E402,F401
