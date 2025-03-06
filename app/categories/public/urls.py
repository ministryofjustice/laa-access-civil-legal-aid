from app.categories.public import bp
from app.categories.results.views import CannotFindYourProblemPage, NextStepsPage
from app.categories.views import CategoryLandingPage, QuestionPage
from app.categories.public.forms import PolicePrisonOrDetentionCentreForm
from app.categories.constants import PUBLIC_LAW


class PublicLandingPage(CategoryLandingPage):
    question_title = PUBLIC_LAW.title
    category = PUBLIC_LAW


bp.add_url_rule(
    "/public-organisations",
    view_func=PublicLandingPage.as_view(
        "landing", template="categories/public/landing.html"
    ),
)

bp.add_url_rule(
    "/public-organisations/reason",
    view_func=QuestionPage.as_view(
        "reason",
        form_class=PolicePrisonOrDetentionCentreForm,
    ),
)
bp.add_url_rule(
    "/public-organisations/cannot-find-your-problem",
    view_func=CannotFindYourProblemPage.as_view(
        "cannot_find_your_problem",
        next_steps_page="categories.public.next_steps",
    ),
)
bp.add_url_rule(
    "/public/next-steps",
    view_func=NextStepsPage.as_view(
        "next_steps",
        category=PUBLIC_LAW,
    ),
)
