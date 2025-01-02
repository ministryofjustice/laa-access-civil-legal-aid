from app.categories.community_care import bp
from app.categories.views import CategoryLandingPage
from app.categories.constants import Category

CATEGORY_NAME = Category.COMMUNITY_CARE

FALA_REDIRECT = {
    "endpoint": "find-a-legal-adviser.search",
    "category": "com",
}


class CommunityCareLandingPage(CategoryLandingPage):
    question_title = CATEGORY_NAME

    category = CATEGORY_NAME

    routing_map = {
        "care_from_council": FALA_REDIRECT,
        "carer": FALA_REDIRECT,
        "receive_care_in_own_home": FALA_REDIRECT,
        "care_or_funding_stops": FALA_REDIRECT,
        "placement_care_homes_care_housing": FALA_REDIRECT,
        "problems_with_quality_of_care": FALA_REDIRECT,
        "care_leaver": FALA_REDIRECT,
        "other": "categories.results.refer",
    }


bp.add_url_rule(
    "/community-care/",
    view_func=CommunityCareLandingPage.as_view(
        "landing", template="categories/community_care/landing.html"
    ),
)

CommunityCareLandingPage.register_routes(blueprint=bp)
