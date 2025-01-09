from app.categories.asylum_immigration import bp
from app.categories.views import CategoryLandingPage
from app.categories.constants import Category


FALA_REDIRECT = {
    "endpoint": "find-a-legal-adviser.search",
    "category": "immas",
}


class AsylumAndImmigrationLandingPage(CategoryLandingPage):
    question_title = "Asylum and immigration"
    category = Category.ASYLUM_AND_IMMIGRATION

    routing_map = {
        "apply": FALA_REDIRECT,
        "housing": "categories.housing.homelessness",
        "domestic_abuse": FALA_REDIRECT,
        "detained": FALA_REDIRECT,
        "modern_slavery": FALA_REDIRECT,
    }


bp.add_url_rule(
    "/asylum-and-immigration",
    view_func=AsylumAndImmigrationLandingPage.as_view(
        "landing", template="categories/asylum-and-immigration/landing.html"
    ),
)

AsylumAndImmigrationLandingPage.register_routes(blueprint=bp)
