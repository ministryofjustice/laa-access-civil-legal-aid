from app.categories.mental_capacity import bp
from app.categories.results.views import CannotFindYourProblemPage, NextStepsPage
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
        "other": "categories.mental_capacity.cannot_find_your_problem",
    }


MentalCapacityLandingPage.register_routes(bp, "mental-capacity-health")
bp.add_url_rule(
    "/mental-capacity-health/cannot-find-your-problem",
    view_func=CannotFindYourProblemPage.as_view(
        "cannot_find_your_problem",
        category=MENTAL_CAPACITY,
        next_steps_page="categories.mental_capacity.next_steps",
    ),
)
bp.add_url_rule(
    "/mental-capacity-health/next-steps",
    view_func=NextStepsPage.as_view(
        "next_steps",
        category=MENTAL_CAPACITY,
    ),
)
