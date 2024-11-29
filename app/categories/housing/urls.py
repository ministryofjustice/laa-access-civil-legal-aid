from app.categories.housing import bp
from app.categories.views import CategoryLandingPage

bp.add_url_rule(
    "/housing/",
    view_func=CategoryLandingPage.as_view("landing", "categories/housing.html"),
)
