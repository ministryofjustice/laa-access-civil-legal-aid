from flask import session, request, after_this_request
from app.main import bp
from datetime import datetime, timedelta, timezone
import uuid
import re
import json


@bp.app_context_processor
def get_gtm_anon_id():
    gtm_anon_id = session.get("gtm_anon_id", "")
    return {"gtm_anon_id": gtm_anon_id}


def get_gtm_anon_id_from_cookie():
    uuid_pattern = re.compile(r"^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$")
    anon_id_cookie = request.cookies.get("gtm_anon_id", default="")
    if not uuid_pattern.match(anon_id_cookie):
        return None
    return anon_id_cookie


@bp.before_app_request
def detect_gtm_anon_id():
    cookies_policy = request.cookies.get("cookies_policy", "{}")

    try:
        policy_dict = json.loads(cookies_policy)
    except ValueError:
        policy_dict = {}

    if policy_dict.get("analytics") != "yes":
        return

    if "gtm_anon_id" in session:
        return

    session["gtm_anon_id"] = str(uuid.uuid4())

    @after_this_request
    def remember_gtm_anon_id(response):
        if not session.get("gtm_anon_id"):
            return
        expiration_date = datetime.now(timezone.utc) + timedelta(days=730)
        response.set_cookie(
            "gtm_anon_id",
            session.get("gtm_anon_id"),
            expires=expiration_date,
        )
        return response
