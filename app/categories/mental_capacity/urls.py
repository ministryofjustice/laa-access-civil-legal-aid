from app.categories.mental_capacity import bp
from app.categories.views import CategoryLandingPage
from app.categories.constants import MENTAL_CAPACITY


class MentalCapacityLandingPage(CategoryLandingPage):
    question_title = MENTAL_CAPACITY.title

    category = MENTAL_CAPACITY

    routing_map = {
        MENTAL_CAPACITY.sub.mental_capacity.code: {
            "endpoint": "find-a-legal-adviser.search",
            "category": "mhe",
            "secondary_category": "com",
        },
        MENTAL_CAPACITY.sub.court_of_protection.code: {
            "endpoint": "find-a-legal-adviser.search",
            "category": "mhe",
            "secondary_category": "com",
        },
        MENTAL_CAPACITY.sub.detention.code: {
            "endpoint": "find-a-legal-adviser.search",
            "category": "mhe",
        },
        # Todo: This needs to be updated to route to the community care landing page once it has been made
        MENTAL_CAPACITY.sub.social_care.code: "categories.community_care.landing",
        "other": "categories.results.refer",
    }


bp.add_url_rule(
    "/mental-capacity-health",
    view_func=MentalCapacityLandingPage.as_view(
        "landing", template="categories/mental_capacity/landing.html"
    ),
)
MentalCapacityLandingPage.register_routes(bp)
