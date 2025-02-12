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
        ASYLUM_AND_IMMIGRATION.sub.apply.code: FALA_REDIRECT,
        ASYLUM_AND_IMMIGRATION.sub.housing.code: "categories.housing.homelessness",
        ASYLUM_AND_IMMIGRATION.sub.domestic_abuse.code: FALA_REDIRECT,
        ASYLUM_AND_IMMIGRATION.sub.detained.code: FALA_REDIRECT,
        ASYLUM_AND_IMMIGRATION.sub.modern_slavery.code: FALA_REDIRECT,
    }


bp.add_url_rule(
    "/asylum-and-immigration",
    view_func=AsylumAndImmigrationLandingPage.as_view(
        "landing", template="categories/asylum-and-immigration/landing.html"
    ),
)

AsylumAndImmigrationLandingPage.register_routes(blueprint=bp)
