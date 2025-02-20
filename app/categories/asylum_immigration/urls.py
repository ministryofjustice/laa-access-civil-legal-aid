from app.categories.asylum_immigration import bp
from app.categories.results.views import CannotFindYourProblemPage, NextStepsPage
from app.categories.views import CategoryLandingPage
from app.categories.constants import ASYLUM_AND_IMMIGRATION


FALA_REDIRECT = {
    "endpoint": "find-a-legal-adviser.search",
    "category": "immas",
}


class AsylumAndImmigrationLandingPage(CategoryLandingPage):
    question_title = ASYLUM_AND_IMMIGRATION.title
    category = ASYLUM_AND_IMMIGRATION

    routing_map = {
        "main": [
            (ASYLUM_AND_IMMIGRATION.sub.apply, FALA_REDIRECT),
            (ASYLUM_AND_IMMIGRATION.sub.housing, "categories.housing.homelessness"),
            (ASYLUM_AND_IMMIGRATION.sub.domestic_abuse, FALA_REDIRECT),
            (ASYLUM_AND_IMMIGRATION.sub.detained, FALA_REDIRECT),
        ],
        "more": [
            (ASYLUM_AND_IMMIGRATION.sub.modern_slavery, FALA_REDIRECT),
        ],
        "other": {"endpoint": "categories.results.refer", "category": "immas"},
    }


AsylumAndImmigrationLandingPage.register_routes(
    blueprint=bp, path="/asylum-and-immigration"
)
bp.add_url_rule(
    "/mental-capacity-health/cannot-find-your-problem",
    view_func=CannotFindYourProblemPage.as_view(
        "cannot_find_your_problem",
        category=ASYLUM_AND_IMMIGRATION,
        next_steps_page="categories.asylum_immigration.next_steps",
    ),
)
bp.add_url_rule(
    "/mental-capacity-health/next-steps",
    view_func=NextStepsPage.as_view(
        "next_steps",
        category=ASYLUM_AND_IMMIGRATION,
    ),
)
