from flask import Blueprint, request, url_for, session
from flask import current_app

bp = Blueprint("main", __name__, template_folder="../templates/main")

from app.main import routes  # noqa: E402,F401
from app.main import filters  # noqa: E402,F401


def get_locale():
    locale = request.cookies.get("locale")
    if locale in current_app.config["LANGUAGES"]:
        return locale

    language_keys = current_app.config["LANGUAGES"].keys()
    return request.accept_languages.best_match(language_keys) or "en"


@bp.app_context_processor
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


@bp.app_context_processor
def inject_exit_this_page():
    category = session.category

    if not category:
        return {"show_exit_this_page": False}

    return {"show_exit_this_page": getattr(category, "exit_page", False)}
