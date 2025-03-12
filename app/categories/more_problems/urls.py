from flask import render_template, url_for
from app.categories.more_problems import bp
from app.categories.views import CategoryPage
from app.categories.results.views import CannotFindYourProblemPage, NextStepsPage
from app.categories.more_problems.constants import (
    ADOPTING,
    WORK_WITH_VULNERABLE,
    ANTI_SOCIAL,
    CLINICAL_NEGLIGENCE,
    COMPENSATION,
    ACCUSED_DA,
    ENVIRONMENTAL_POLLUTION,
    FGM,
    FORCED_MARRIAGE,
    INQUEST,
    MENTAL_HEALTH,
    CRIME_ACT,
    TERRORISM,
    TRAFFICKING,
)


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
            (ACCUSED_DA, url_for("categories.domestic_abuse.accused_da")),
            (
                ENVIRONMENTAL_POLLUTION,
                url_for("find-a-legal-adviser.search", category="pub"),
            ),
            (FGM, url_for("categories.domestic_abuse.fgm")),
            (FORCED_MARRIAGE, url_for("categories.domestic_abuse.forced_marriage")),
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
