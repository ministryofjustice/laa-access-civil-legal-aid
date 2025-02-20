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
bp.add_url_rule(
    "/cannot-find-problem",
    view_func=ResultPage.as_view(
        "cannot_find_problem",
        get_help_organisations=False,
    ),
)
bp.add_url_rule(
    "/next-steps-get-help",
    view_func=ResultPage.as_view(
        "next_steps",
        get_help_organisations=True,
    ),
)
