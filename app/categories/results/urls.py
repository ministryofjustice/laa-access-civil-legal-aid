from app.categories.results import bp
from app.categories.views import CategoryPage
from app.categories.results.views import HlpasInScopePage

bp.add_url_rule(
    "/legal-aid-available",
    view_func=CategoryPage.as_view("in_scope", template="categories/in-scope.html"),
)
bp.add_url_rule(
    "/legal-aid-available-hlpas",
    view_func=HlpasInScopePage.as_view(
        "in_scope_hlpas", template="categories/in-scope.html"
    ),
)
bp.add_url_rule(
    "/alternative-help",
    view_func=CategoryPage.as_view(
        "alternative_help", template="categories/alternative-help.html"
    ),
)
