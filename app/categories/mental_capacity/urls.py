from app.categories.mental_capacity import bp
from app.categories.views import CategoryLandingPage
from app.categories.constants import MENTAL_CAPACITY


class MentalCapacityLandingPage(CategoryLandingPage):
    question_title = MENTAL_CAPACITY.title

    category = MENTAL_CAPACITY

    routing_map = {
        "main": [
            (
                MENTAL_CAPACITY.sub.mental_capacity,
                {
                    "endpoint": "find-a-legal-adviser.search",
                    "category": "mhe",
                    "secondary_category": "com",
                },
            ),
            (
                MENTAL_CAPACITY.sub.court_of_protection,
                {
                    "endpoint": "find-a-legal-adviser.search",
                    "category": "mhe",
                    "secondary_category": "com",
                },
            ),
            (
                MENTAL_CAPACITY.sub.detention,
                {
                    "endpoint": "find-a-legal-adviser.search",
                    "category": "mhe",
                },
            ),
            # Todo: # This needs to be updated to route to the community care landing page once it has been made
            (MENTAL_CAPACITY.sub.social_care, "categories.community_care.landing"),
        ],
        "more": [],
        "other": "categories.results.cannot_find_problem",
    }


MentalCapacityLandingPage.register_routes(bp, "mental-capacity-health")
