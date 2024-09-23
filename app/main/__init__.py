from flask import Blueprint, request, url_for
from flask import current_app

bp = Blueprint("main", __name__, template_folder="../templates/main")

from app.main import routes  # noqa: E402,F401
from app.main import filters  # noqa: E402,F401


def get_locale():
    if request and request.cookies.get("locale"):
        return request.cookies.get("locale")

    language_keys = [key for key, _ in current_app.config["LANGUAGES"]]
    return request.accept_languages.best_match(language_keys) or "en"


@bp.context_processor
def inject_language_switcher():
    locale = get_locale()
    code = "cy" if locale == "en" else "en"
    text = "Cymraeg" if locale == "en" else "English"
    return {
        "language": {
            "current": locale,
            "switch": {
                "href": url_for("main.set_locale", locale=code),
                "text": text,
            },
        }
    }
