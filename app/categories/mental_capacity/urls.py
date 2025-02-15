from app.categories.mental_capacity import bp
from app.categories.views import CategoryLandingPage
from app.categories.constants import MENTAL_CAPACITY


class MentalCapacityLandingPage(CategoryLandingPage):
    question_title = "Mental capacity, mental health"

    category = MENTAL_CAPACITY

    routing_map = {
        "mental_capacity": {
            "endpoint": "find-a-legal-adviser.search",
            "category": "mhe",
            "secondary_category": "com",
        },
        "court_of_protection": {
            "endpoint": "find-a-legal-adviser.search",
            "category": "mhe",
            "secondary_category": "com",
        },
        "detention": {"endpoint": "find-a-legal-adviser.search", "category": "mhe"},
        "social_care": "categories.community_care.landing",
        "other": "categories.results.refer",
    }


bp.add_url_rule(
    "/mental-capacity-health",
    view_func=MentalCapacityLandingPage.as_view(
        "landing", template="categories/mental_capacity/landing.html"
    ),
)
MentalCapacityLandingPage.register_routes(bp)
