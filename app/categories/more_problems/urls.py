from flask import render_template, url_for, session
from app.categories.more_problems import bp
from app.categories.views import CategoryPage
from app.categories.results.views import CannotFindYourProblemPage, NextStepsPage
from app.categories.more_problems.constants import (
    ADOPTING,
    WORK_WITH_VULNERABLE,
    ANTI_SOCIAL,
    CLINICAL_NEGLIGENCE,
    COMPENSATION,
    ENVIRONMENTAL_POLLUTION,
    INQUEST,
    MENTAL_HEALTH,
    CRIME_ACT,
    TERRORISM,
    TRAFFICKING,
)
from app.categories.constants import DOMESTIC_ABUSE


class MoreProblemsPage(CategoryPage):
    template = "categories/more-problems.html"

    def dispatch_request(self):
        listing = [
            (ADOPTING, url_for("find-a-legal-adviser.search", category="mat")),
            (WORK_WITH_VULNERABLE, url_for("find-a-legal-adviser.search")),
            (ANTI_SOCIAL, url_for("categories.x_cat.landlord-council")),
            (
                CLINICAL_NEGLIGENCE,
                url_for("find-a-legal-adviser.search", category="med"),
            ),
            (COMPENSATION, url_for("find-a-legal-adviser.search", category="aap")),
            (
                DOMESTIC_ABUSE.sub.accused_of_domestic_abuse,
                url_for("categories.domestic_abuse.accused_of_domestic_abuse"),
            ),
            (
                ENVIRONMENTAL_POLLUTION,
                url_for("find-a-legal-adviser.search", category="pub"),
            ),
            (DOMESTIC_ABUSE.sub.fgm, url_for("categories.domestic_abuse.fgm")),
            (
                DOMESTIC_ABUSE.sub.forced_marriage,
                url_for("categories.domestic_abuse.forced_marriage"),
            ),
            (INQUEST, url_for("find-a-legal-adviser.search")),
            (MENTAL_HEALTH, url_for("find-a-legal-adviser.search", category="mhe")),
            (CRIME_ACT, url_for("find-a-legal-adviser.search", category="crm")),
            (
                TERRORISM,
                url_for(
                    "find-a-legal-adviser.search",
                    category="immas",
                    secondary_category="pub",
                ),
            ),
            (TRAFFICKING, url_for("find-a-legal-adviser.search", category="immas")),
        ]
        """
        Used to ensure that the exit page does not persist and user cannot select
        multiple subcategories
        """
        if session.get("category", {}):
            session.pop("category")
        if session.get("category_answers", {}):
            session["category_answers"] = []

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
