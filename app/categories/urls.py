from app.categories import bp
from app.categories.views import CategoryPage, IndexPage

bp.add_url_rule(
    "/", view_func=IndexPage.as_view("index", template="categories/index.html")
)
bp.add_url_rule(
    "/legal-aid-available",
    view_func=CategoryPage.as_view("in_scope", template="categories/in-scope.html"),
)
bp.add_url_rule(
    "/alternative-help",
    view_func=CategoryPage.as_view(
        "alternative_help", template="categories/alternative-help.html"
    ),
)
bp.add_url_rule(
    "/more-problems",
    view_func=CategoryPage.as_view(
        "more_problems", template="categories/more-problems.html"
    ),
)
