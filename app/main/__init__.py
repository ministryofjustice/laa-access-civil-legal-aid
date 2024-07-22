from flask import Blueprint, session, request, after_this_request
from datetime import datetime, timedelta, UTC
import re
import uuid

bp = Blueprint("main", __name__, template_folder="../templates/main")

from app.main import routes  # noqa: E402,F401


def get_gtm_anon_id():
    gtm_anon_id = session.get("gtm_anon_id", "")
    return {"gtm_anon_id": gtm_anon_id}


def get_gtm_anon_id_from_cookie():
    uuid_pattern = re.compile(r"^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$")
    anon_id_cookie = request.cookies.get("gtm_anon_id")
    if not uuid_pattern.match(anon_id_cookie):
        return None
    return anon_id_cookie


@bp.before_app_request
def detect_gtm_anon_id():
    # gtm_anon_id is used to track user anonymously across services for Google Tag Manager.
    if "gtm_anon_id" in session:
        return

    anon_id_cookie = get_gtm_anon_id_from_cookie()
    if anon_id_cookie:
        session["gtm_anon_id"] = anon_id_cookie
        return

    @after_this_request
    def remember_gtm_anon_id(response):
        session["gtm_anon_id"] = str(uuid.uuid4())
        expiration_date = datetime.now(UTC) + timedelta(days=30)
        response.set_cookie("gtm_anon_id", session.get("gtm_anon_id"), expires=expiration_date)
        return response
