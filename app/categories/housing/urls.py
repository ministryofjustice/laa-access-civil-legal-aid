from app.categories.housing import bp
from app.categories.results.views import CannotFindYourProblemPage, NextStepsPage
from app.categories.views import CategoryLandingPage
from app.categories.constants import HOUSING


class HousingLandingPage(CategoryLandingPage):
    question_title = HOUSING.title

    category = HOUSING

    routing_map = {
        "main": [
            (HOUSING.sub.homelessness, "categories.results.in_scope_hlpas"),
            (HOUSING.sub.eviction, "categories.results.in_scope_hlpas"),
            (HOUSING.sub.forced_to_sell, "categories.results.in_scope_hlpas"),
            (HOUSING.sub.repairs, "categories.results.in_scope"),
            (HOUSING.sub.council_housing, "categories.results.in_scope"),
        ],
        "more": [
            (HOUSING.sub.threatened, "categories.results.in_scope"),
            (HOUSING.sub.asylum_seeker, "categories.results.in_scope"),
            (HOUSING.sub.discrimination, "categories.discrimination.where"),
            (HOUSING.sub.antisocial_behaviour, "categories.results.in_scope"),
        ],
        "other": "categories.housing.cannot_find_your_problem",
    }


HousingLandingPage.register_routes(bp)
bp.add_url_rule(
    "/housing/cannot-find-your-problem",
    view_func=CannotFindYourProblemPage.as_view(
        "cannot_find_your_problem",
        category=HOUSING,
        next_steps_page="categories.housing.next_steps",
    ),
)
bp.add_url_rule(
    "/housing/next-steps",
    view_func=NextStepsPage.as_view(
        "next_steps",
        category=HOUSING,
    ),
)
