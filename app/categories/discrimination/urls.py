from . import bp
from .forms import (
    DiscriminationWhereForm,
    DiscriminationWhyForm,
    DiscriminationAreYouUnder18Form,
)
from ..constants import DISCRIMINATION
from ..results.views import CannotFindYourProblemPage, NextStepsPage
from ..views import QuestionPage

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
