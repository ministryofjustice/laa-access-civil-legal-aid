from app.categories.results import bp
from app.categories.results.views import HlpasInScopePage, ResultPage

bp.add_url_rule(
    "/legal-aid-available",
    view_func=ResultPage.as_view("in_scope", template="categories/in-scope.html"),
)
bp.add_url_rule(
    "/legal-aid-available-hlpas",
    view_func=HlpasInScopePage.as_view(
        "in_scope_hlpas", template="categories/in-scope.html"
    ),
)
bp.add_url_rule(
    "/refer",
    view_func=ResultPage.as_view("refer", template="categories/refer.html"),
)
