from app.categories.housing import bp
from app.categories.views import CategoryLandingPage
from app.categories.constants import HOUSING


class HousingLandingPage(CategoryLandingPage):
    question_title = HOUSING.title

    category = HOUSING

    routing_map = {
        HOUSING.sub.homelessness.code: "categories.results.in_scope_hlpas",
        HOUSING.sub.eviction.code: "categories.results.in_scope_hlpas",
        HOUSING.sub.forced_to_sell.code: "categories.results.in_scope_hlpas",
        HOUSING.sub.repairs.code: "categories.results.in_scope",
        HOUSING.sub.council_housing.code: "categories.results.in_scope",
        HOUSING.sub.threatened.code: "categories.results.in_scope",
        HOUSING.sub.asylum_seeker.code: "categories.results.in_scope",
        HOUSING.sub.discrimination.code: "categories.discrimination.where",
        HOUSING.sub.antisocial_behaviour.code: "categories.results.in_scope",
        "other": "categories.results.refer",
    }


bp.add_url_rule(
    "/housing",
    view_func=HousingLandingPage.as_view(
        "landing", template="categories/housing/landing.html"
    ),
)
HousingLandingPage.register_routes(bp)
