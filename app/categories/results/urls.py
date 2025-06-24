from app.categories.results import bp
from app.categories.results.views import (
    ResultPage,
    CannotFindYourProblemPage,
    NextStepsPage,
)
from app.categories.mixins import InScopeMixin


class InScopeResultPage(InScopeMixin, ResultPage):
    pass


bp.add_url_rule(
    "/legal-aid-available",
    view_func=InScopeResultPage.as_view("in_scope", template="categories/in-scope.html"),
)
bp.add_url_rule(
    "/cannot-find-your-problem",
    view_func=CannotFindYourProblemPage.as_view(
        "cannot_find_your_problem",
    ),
)
bp.add_url_rule(
    "/next-steps",
    view_func=NextStepsPage.as_view(
        "next_steps",
        get_help_organisations=False,
    ),
)
