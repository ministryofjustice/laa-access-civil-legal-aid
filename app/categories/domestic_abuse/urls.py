from app.categories.domestic_abuse import bp
from app.categories.domestic_abuse.forms import WorriedAboutSomeonesSafetyForm
from app.categories.results.views import CannotFindYourProblemPage, NextStepsPage
from app.categories.views import (
    QuestionPage,
    CategoryLandingPage,
    CategoryAnswerPage,
    CategoryAnswer,
)
from app.categories.constants import DOMESTIC_ABUSE, HOUSING
from app.categories.models import QuestionType


class DomesticAbuseLandingPage(CategoryLandingPage):
    question_title = DOMESTIC_ABUSE.title

    category = DOMESTIC_ABUSE
    routing_map = {
        "main": [
            (
                DOMESTIC_ABUSE.sub.protect_you_and_your_children,
                "categories.domestic_abuse.are_you_at_risk_of_harm",
            ),
            (
                DOMESTIC_ABUSE.sub.leaving_an_abusive_relationship,
                "categories.domestic_abuse.are_you_at_risk_of_harm",
            ),
            (
                DOMESTIC_ABUSE.sub.problems_with_ex_partner,
                "categories.domestic_abuse.are_you_at_risk_of_harm",
            ),
        ],
        "more": [
            (
                DOMESTIC_ABUSE.sub.forced_marriage,
                "categories.domestic_abuse.are_you_at_risk_of_harm",
            ),
            (
                DOMESTIC_ABUSE.sub.fgm,
                "categories.domestic_abuse.are_you_at_risk_of_harm",
            ),
            (
                HOUSING.sub.problems_with_neighbours,
                {
                    "endpoint": "contact.contact_us_fast_tracked",
                    "reason": "more-info-required",
                },
            ),
            (
                DOMESTIC_ABUSE.sub.housing_homelessness_losing_home,
                "categories.housing.landing",
            ),
        ],
        "other": "categories.domestic_abuse.cannot_find_your_problem",
    }


DomesticAbuseLandingPage.register_routes(bp)
bp.add_url_rule(
    "/domestic-abuse/accused-da",
    view_func=CategoryAnswerPage.as_view(
        "accused_of_domestic_abuse",
        category_answer=CategoryAnswer(
            question="more_problems",
            answer_value=DOMESTIC_ABUSE.sub.accused_of_domestic_abuse.code,
            answer_label=DOMESTIC_ABUSE.sub.accused_of_domestic_abuse.title,
            category=DOMESTIC_ABUSE.sub.accused_of_domestic_abuse,
            question_page="categories.more_problems.landing",
            next_page="categories.results.in_scope",
            question_type=QuestionType.SUB_CATEGORY,
        ),
    ),
)
bp.add_url_rule(
    "/domestic-abuse/are-you-at-risk-of-harm",
    view_func=QuestionPage.as_view(
        "are_you_at_risk_of_harm", form_class=WorriedAboutSomeonesSafetyForm
    ),
)
bp.add_url_rule(
    "/domestic-abuse/cannot-find-your-problem",
    view_func=CannotFindYourProblemPage.as_view(
        "cannot_find_your_problem",
        category=DOMESTIC_ABUSE,
        next_steps_page="categories.domestic_abuse.next_steps",
    ),
)
bp.add_url_rule(
    "/domestic-abuse/next-steps",
    view_func=NextStepsPage.as_view(
        "next_steps",
        category=DOMESTIC_ABUSE,
    ),
)
