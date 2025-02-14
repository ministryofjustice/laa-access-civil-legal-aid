from app.categories.community_care import bp
from app.categories.views import CategoryLandingPage
from app.categories.constants import COMMUNITY_CARE


FALA_REDIRECT = {
    "endpoint": "find-a-legal-adviser.search",
    "category": "com",
}


class CommunityCareLandingPage(CategoryLandingPage):
    question_title = COMMUNITY_CARE.title

    category = COMMUNITY_CARE

    routing_map = {
        "main": [
            (COMMUNITY_CARE.sub.care_from_council, FALA_REDIRECT),
            (COMMUNITY_CARE.sub.carer, FALA_REDIRECT),
            (COMMUNITY_CARE.sub.receive_care_in_own_home, FALA_REDIRECT),
            (COMMUNITY_CARE.sub.care_or_funding_stops, FALA_REDIRECT),
            (COMMUNITY_CARE.sub.placement_care_homes_care_housing, FALA_REDIRECT),
            (COMMUNITY_CARE.sub.problems_with_quality_of_care, FALA_REDIRECT),
            (COMMUNITY_CARE.sub.care_leaver, FALA_REDIRECT),
        ],
        "more": [],
        "other": "categories.results.refer",
    }


CommunityCareLandingPage.register_routes_2(blueprint=bp)
