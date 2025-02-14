from app.categories.housing import bp
from app.categories.views import CategoryLandingPage
from app.categories.constants import HOUSING


class HousingLandingPage(CategoryLandingPage):
    question_title = HOUSING.title

    category = HOUSING

    routing_map = {
        "main": [
            (HOUSING.sub.homelessness, "categories.results.in_scope_hlpas"),
            (HOUSING.sub.eviction, "categories.results.in_scope_hlpas"),
            (HOUSING.sub.forced_to_sell, "categories.results.in_scope_hlpas"),
            (HOUSING.sub.repairs, "categories.results.in_scope"),
            (HOUSING.sub.council_housing, "categories.results.in_scope"),
        ],
        "more": [
            (HOUSING.sub.threatened, "categories.results.in_scope"),
            (HOUSING.sub.asylum_seeker, "categories.results.in_scope"),
            (HOUSING.sub.discrimination, "categories.discrimination.where"),
            (HOUSING.sub.antisocial_behaviour, "categories.results.in_scope"),
        ],
        "other": "categories.results.refer",
    }


HousingLandingPage.register_routes_2(bp)
