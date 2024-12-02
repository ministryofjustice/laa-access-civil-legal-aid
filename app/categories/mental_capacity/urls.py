from app.categories.mental_capacity import bp
from app.categories.views import CategoryLandingPage


class MentalCapacityLandingPage(CategoryLandingPage):
    question_title = "Mental capacity, mental health"

    category = "Mental Capacity"

    routing_map = {
        "mental_capacity": {
            "endpoint": "find-a-legal-adviser.search",
            "category": "med",
            "secondary_category": "deb",
        },
        "court_of_protection": "categories.results.in_scope_hlpas",
        "detention": "categories.results.in_scope_hlpas",
        "social_care": "categories.results.in_scope",
        "other": "categories.results.refer",
    }


bp.add_url_rule(
    "/mental-capacity-health",
    view_func=MentalCapacityLandingPage.as_view(
        "landing", template="categories/mental_capacity/landing.html"
    ),
)
MentalCapacityLandingPage.register_routes(bp)
