from flask import Blueprint
import requests

from app.find_a_legal_adviser.laalaa import laalaa_url, get_category_name

bp = Blueprint("find-a-legal-adviser", __name__)

bp.add_app_template_filter(get_category_name, "category_name")

from app.find_a_legal_adviser import routes  # noqa: E402,F401


def get_categories():
    response = requests.get(laalaa_url(endpoint="categories_of_law"))
    return response.json()


@bp.record_once
def on_blueprint_init(state):
    # Initialize categories when blueprint is registered
    app = state.app
    with app.app_context():
        bp.categories = get_categories()
