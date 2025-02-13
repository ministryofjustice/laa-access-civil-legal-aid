from app.categories.asylum_immigration import bp
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


AsylumAndImmigrationLandingPage.register_routes_2(
    blueprint=bp, path="/asylum-and-immigration"
)
