from flask import redirect, url_for
from . import bp
from .forms import (
    DiscriminationWhereForm,
    DiscriminationWhyForm,
    DiscriminationAreYouUnder18Form,
)
from ..constants import DISCRIMINATION
from ..results.views import CannotFindYourProblemPage, NextStepsPage
from ..views import QuestionPage, CategoryLandingPage


class DiscriminationCategoryLandingPage(CategoryLandingPage):
    category = DISCRIMINATION

    def __init__(self):
        super().__init__(
            template=None,
        )

    def dispatch_request(self):
        self.set_category_answer()
        return redirect(url_for("categories.discrimination.where"))


bp.add_url_rule("/discrimination/", view_func=DiscriminationCategoryLandingPage.as_view("landing"))
bp.add_url_rule(
    "/discrimination/where",
    view_func=QuestionPage.as_view("where", form_class=DiscriminationWhereForm),
)
bp.add_url_rule(
    "/discrimination/why",
    view_func=QuestionPage.as_view("why", form_class=DiscriminationWhyForm),
)
bp.add_url_rule(
    "/discrimination/age",
    view_func=QuestionPage.as_view(
        "age",
        form_class=DiscriminationAreYouUnder18Form,
    ),
)
bp.add_url_rule(
    "/discrimination/cannot-find-your-problem",
    view_func=CannotFindYourProblemPage.as_view(
        "cannot_find_your_problem",
        category=DISCRIMINATION,
        next_steps_page="categories.discrimination.next_steps",
    ),
)
bp.add_url_rule(
    "/discrimination/next-steps",
    view_func=NextStepsPage.as_view(
        "next_steps",
        category=DISCRIMINATION,
    ),
)
