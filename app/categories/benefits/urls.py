from . import bp
from .forms import AppealQuestionForm
from ..constants import BENEFITS
from ..results.views import CannotFindYourProblemPage, NextStepsPage
from ..views import QuestionPage

bp.add_url_rule(
    "/benefits/appeal",
    view_func=QuestionPage.as_view(
        "appeal",
        form_class=AppealQuestionForm,
        template="categories/benefits/appeal.html",
    ),
)
bp.add_url_rule(
    "/benefits/cannot-find-your-problem",
    view_func=CannotFindYourProblemPage.as_view(
        "cannot_find_your_problem",
        category=BENEFITS,
        next_steps_page="categories.benefits.next_steps",
    ),
)
bp.add_url_rule(
    "/benefits/next-steps",
    view_func=NextStepsPage.as_view(
        "next_steps",
        category=BENEFITS,
    ),
)
