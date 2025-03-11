from flask import render_template
from app.categories.more_problems import bp
from app.categories.views import CategoryPage
from app.categories.results.views import CannotFindYourProblemPage, NextStepsPage
from app.categories.more_problems.constants import MORE_PROBLEMS


class MoreProblemsPage(CategoryPage):
    template = "categories/more-problems.html"

    def dispatch_request(self):
        listing = MORE_PROBLEMS
        return render_template(self.template, listing=listing)


bp.add_url_rule(
    "/more-problems",
    view_func=MoreProblemsPage.as_view(
        "landing", template="categories/more-problems.html"
    ),
)
bp.add_url_rule(
    "/more-problems/cannot-find-your-problem",
    view_func=CannotFindYourProblemPage.as_view(
        "cannot_find_your_problem",
        next_steps_page="categories.more_problems.next_steps",
    ),
)
bp.add_url_rule(
    "/more-problems/next-steps",
    view_func=NextStepsPage.as_view(
        "next_steps",
    ),
)
