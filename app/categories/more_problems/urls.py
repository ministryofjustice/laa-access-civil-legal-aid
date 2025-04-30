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
    MENTAL_HEALTH,
    CRIME_ACT,
    TERRORISM,
    TRAFFICKING,
)
from app.categories.models import QuestionType


class MoreProblemsPage(CategoryPage):
    template = "categories/more-problems.html"

    def dispatch_request(self):
        listing = [
            (ADOPTING, url_for("categories.more_problems.adopting")),
            (
                WORK_WITH_VULNERABLE,
                url_for("categories.more_problems.work_with_vulnerable"),
            ),
            (
                HOUSING.sub.antisocial_behaviour_gangs,
                url_for("categories.housing.accused_of_anti_social_behaviour"),
            ),
            (
                CLINICAL_NEGLIGENCE,
                url_for("categories.more_problems.clinical_negligence"),
            ),
            (COMPENSATION, url_for("categories.more_problems.compensation")),
            (
                DOMESTIC_ABUSE.sub.accused_of_domestic_abuse,
                url_for("categories.domestic_abuse.accused_of_domestic_abuse"),
            ),
            (
                ENVIRONMENTAL_POLLUTION,
                url_for("categories.more_problems.environmental_pollution"),
            ),
            (DOMESTIC_ABUSE.sub.fgm, url_for("categories.domestic_abuse.fgm")),
            (
                DOMESTIC_ABUSE.sub.forced_marriage,
                url_for("categories.domestic_abuse.forced_marriage"),
            ),
            (INQUEST, url_for("categories.more_problems.inquest")),
            (MENTAL_HEALTH, url_for("categories.more_problems.mental_health")),
            (CRIME_ACT, url_for("categories.more_problems.crime_act")),
            (TERRORISM, url_for("categories.more_problems.terrorism")),
            (TRAFFICKING, url_for("categories.more_problems.trafficking")),
        ]
        """
        Used to ensure that the exit page does not persist and user cannot select
        multiple subcategories
        """
        session.clear_category()

        return render_template(self.template, listing=listing)


bp.add_url_rule(
    "/more-problems",
    view_func=MoreProblemsPage.as_view(
        "landing", template="categories/more-problems.html"
    ),
)
bp.add_url_rule(
    "/more-problems/adopting",
    view_func=CategoryAnswerPage.as_view(
        "adopting",
        category_answer=CategoryAnswer(
            question="more_problems",
            answer_value=ADOPTING.code,
            answer_label=ADOPTING.title,
            category=ADOPTING,
            question_page="categories.more_problems.landing",
            next_page={"endpoint": "find-a-legal-adviser.search", "category": "mat"},
            question_type=QuestionType.SUB_CATEGORY,
        ),
    ),
)
bp.add_url_rule(
    "/more-problems/work-with-vulnerable",
    view_func=CategoryAnswerPage.as_view(
        "work_with_vulnerable",
        category_answer=CategoryAnswer(
            question="more_problems",
            answer_value=WORK_WITH_VULNERABLE.code,
            answer_label=WORK_WITH_VULNERABLE.title,
            category=WORK_WITH_VULNERABLE,
            question_page="categories.more_problems.landing",
            next_page="find-a-legal-adviser.search",
            question_type=QuestionType.SUB_CATEGORY,
        ),
    ),
)
bp.add_url_rule(
    "/more-problems/clinical-negligence",
    view_func=CategoryAnswerPage.as_view(
        "clinical_negligence",
        category_answer=CategoryAnswer(
            question="more_problems",
            answer_value=CLINICAL_NEGLIGENCE.code,
            answer_label=CLINICAL_NEGLIGENCE.title,
            category=CLINICAL_NEGLIGENCE,
            question_page="categories.more_problems.landing",
            next_page={"endpoint": "find-a-legal-adviser.search", "category": "med"},
            question_type=QuestionType.SUB_CATEGORY,
        ),
    ),
)
bp.add_url_rule(
    "/more-problems/compensation",
    view_func=CategoryAnswerPage.as_view(
        "compensation",
        category_answer=CategoryAnswer(
            question="more_problems",
            answer_value=COMPENSATION.code,
            answer_label=COMPENSATION.title,
            category=COMPENSATION,
            question_page="categories.more_problems.landing",
            next_page={"endpoint": "find-a-legal-adviser.search", "category": "aap"},
            question_type=QuestionType.SUB_CATEGORY,
        ),
    ),
)
bp.add_url_rule(
    "/more-problems/environmental-pollution",
    view_func=CategoryAnswerPage.as_view(
        "environmental_pollution",
        category_answer=CategoryAnswer(
            question="more_problems",
            answer_value=ENVIRONMENTAL_POLLUTION.code,
            answer_label=ENVIRONMENTAL_POLLUTION.title,
            category=ENVIRONMENTAL_POLLUTION,
            question_page="categories.more_problems.landing",
            next_page={"endpoint": "find-a-legal-adviser.search", "category": "pub"},
            question_type=QuestionType.SUB_CATEGORY,
        ),
    ),
)
bp.add_url_rule(
    "/more-problems/inquest",
    view_func=CategoryAnswerPage.as_view(
        "inquest",
        category_answer=CategoryAnswer(
            question="more_problems",
            answer_value=INQUEST.code,
            answer_label=INQUEST.title,
            category=INQUEST,
            question_page="categories.more_problems.landing",
            next_page="find-a-legal-adviser.search",
            question_type=QuestionType.SUB_CATEGORY,
        ),
    ),
)
bp.add_url_rule(
    "/more-problems/mental-health",
    view_func=CategoryAnswerPage.as_view(
        "mental_health",
        category_answer=CategoryAnswer(
            question="more_problems",
            answer_value=MENTAL_HEALTH.code,
            answer_label=MENTAL_HEALTH.title,
            category=MENTAL_HEALTH,
            question_page="categories.more_problems.landing",
            next_page={"endpoint": "find-a-legal-adviser.search", "category": "mhe"},
            question_type=QuestionType.SUB_CATEGORY,
        ),
    ),
)
bp.add_url_rule(
    "/more-problems/crime-act",
    view_func=CategoryAnswerPage.as_view(
        "crime_act",
        category_answer=CategoryAnswer(
            question="more_problems",
            answer_value=CRIME_ACT.code,
            answer_label=CRIME_ACT.title,
            category=CRIME_ACT,
            question_page="categories.more_problems.landing",
            next_page={"endpoint": "find-a-legal-adviser.search", "category": "crm"},
            question_type=QuestionType.SUB_CATEGORY,
        ),
    ),
)
bp.add_url_rule(
    "/more-problems/terrorism",
    view_func=CategoryAnswerPage.as_view(
        "terrorism",
        category_answer=CategoryAnswer(
            question="more_problems",
            answer_value=TERRORISM.code,
            answer_label=TERRORISM.title,
            category=TERRORISM,
            question_page="categories.more_problems.landing",
            next_page={
                "endpoint": "find-a-legal-adviser.search",
                "category": "immas",
                "secondary_category": "pub",
            },
            question_type=QuestionType.SUB_CATEGORY,
        ),
    ),
)
bp.add_url_rule(
    "/more-problems/trafficking",
    view_func=CategoryAnswerPage.as_view(
        "trafficking",
        category_answer=CategoryAnswer(
            question="more_problems",
            answer_value=TRAFFICKING.code,
            answer_label=TRAFFICKING.title,
            category=TRAFFICKING,
            question_page="categories.more_problems.landing",
            next_page={"endpoint": "find-a-legal-adviser.search", "category": "immas"},
            question_type=QuestionType.SUB_CATEGORY,
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
