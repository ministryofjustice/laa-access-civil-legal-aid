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
        COMMUNITY_CARE.sub.care_from_council.code: FALA_REDIRECT,
        COMMUNITY_CARE.sub.carer.code: FALA_REDIRECT,
        COMMUNITY_CARE.sub.receive_care_in_own_home.code: FALA_REDIRECT,
        COMMUNITY_CARE.sub.care_or_funding_stops.code: FALA_REDIRECT,
        COMMUNITY_CARE.sub.placement_care_homes_care_housing.code: FALA_REDIRECT,
        COMMUNITY_CARE.sub.problems_with_quality_of_care.code: FALA_REDIRECT,
        COMMUNITY_CARE.sub.care_leaver.code: FALA_REDIRECT,
        "other": "categories.results.cannot_find_problem",
    }


bp.add_url_rule(
    "/community-care/",
    view_func=CommunityCareLandingPage.as_view(
        "landing", template="categories/community_care/landing.html"
    ),
)

CommunityCareLandingPage.register_routes(blueprint=bp)
