from flask import render_template, url_for, session
from app.categories.more_problems import bp
from app.categories.views import CategoryPage, CategoryAnswerPage, CategoryAnswer
from app.categories.results.views import CannotFindYourProblemPage, NextStepsPage
from app.categories.constants import (
    DOMESTIC_ABUSE,
    HOUSING,
    ADOPTING,
    WORK_WITH_VULNERABLE,
    CLINICAL_NEGLIGENCE,
    COMPENSATION,
    ENVIRONMENTAL_POLLUTION,
    INQUEST,
    MENTAL_HEALTH_DETENTION,
    CRIME_ACT,
    TERRORISM,
    TRAFFICKING,
)
from app.categories.models import QuestionType


class MoreProblemsPage(CategoryPage):
    template = "categories/more-problems.html"

    listing = [
        (
            ADOPTING,
            "categories.more_problems.adopting",
            {"endpoint": "find-a-legal-adviser.search", "category": "mat"},
        ),
        (
            WORK_WITH_VULNERABLE,
            "categories.more_problems.work_with_vulnerable",
            "find-a-legal-adviser.search",
        ),
        (
            HOUSING.sub.antisocial_behaviour_gangs,
            "categories.housing.accused_of_anti_social_behaviour",
            "_",
        ),
        (
            CLINICAL_NEGLIGENCE,
            "categories.more_problems.clinical_negligence",
            {"endpoint": "find-a-legal-adviser.search", "category": "med"},
        ),
        (
            COMPENSATION,
            "categories.more_problems.compensation",
            {"endpoint": "find-a-legal-adviser.search", "category": "aap"},
        ),
        (
            DOMESTIC_ABUSE.sub.accused_of_domestic_abuse,
            "categories.domestic_abuse.accused_of_domestic_abuse",
            "_",
        ),
        (
            ENVIRONMENTAL_POLLUTION,
            "categories.more_problems.environmental_pollution",
            {"endpoint": "find-a-legal-adviser.search", "category": "pub"},
        ),
        (DOMESTIC_ABUSE.sub.fgm, "categories.domestic_abuse.fgm", "_"),
        (
            DOMESTIC_ABUSE.sub.forced_marriage,
            "categories.domestic_abuse.forced_marriage",
            "_",
        ),
        (INQUEST, "categories.more_problems.inquest", "find-a-legal-adviser.search"),
        (
            MENTAL_HEALTH_DETENTION,
            "categories.more_problems.mental_health_detention",
            {"endpoint": "find-a-legal-adviser.search", "category": "mhe"},
        ),
        (
            CRIME_ACT,
            "categories.more_problems.crime_act",
            {"endpoint": "find-a-legal-adviser.search", "category": "crm"},
        ),
        (
            TERRORISM,
            "categories.more_problems.terrorism",
            {
                "endpoint": "find-a-legal-adviser.search",
                "category": "immas",
                "secondary_category": "pub",
            },
        ),
        (
            TRAFFICKING,
            "categories.more_problems.tracking_modern_slavery",
            {"endpoint": "find-a-legal-adviser.search", "category": "immas"},
        ),
    ]

    def get_listing(self):
        return [(cat, url_for(endpoint)) for cat, endpoint, _ in self.listing]

    def dispatch_request(self):
        """
        Used to ensure that the exit page does not persist and user cannot select
        multiple subcategories
        """
        session.clear_category()

        return render_template(self.template, listing=self.get_listing())


bp.add_url_rule(
    "/more-problems",
    view_func=MoreProblemsPage.as_view("landing", template="categories/more-problems.html"),
)

for category, endpoint, next_page in MoreProblemsPage.listing:
    if "categories.more_problems." in endpoint:
        bp.add_url_rule(
            f"/more-problems/{category.url_friendly_name}",
            view_func=CategoryAnswerPage.as_view(
                category.code,
                category_answer=CategoryAnswer(
                    question="more_problems",
                    answer_value=category.code,
                    answer_label=category.title,
                    category=category,
                    question_page="categories.more_problems.landing",
                    next_page=next_page,
                    question_type=QuestionType.CATEGORY,
                ),
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
