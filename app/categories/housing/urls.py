from app.categories.housing import bp
from app.categories.views import CategoryLandingPage


class HousingLandingPage(CategoryLandingPage):
    template = "categories/housing/landing.html"

    question_title = "Housing, Homelessness, and Eviction"

    category = "Housing"

    routing_map = {
        "homelessness": "categories.results.in_scope_hlpas",
        "eviction": "categories.results.in_scope_hlpas",
        "forced_to_sell": "categories.results.in_scope_hlpas",
        "repairs": "categories.results.in_scope",
        "council_housing": "categories.results.in_scope",
        "threatened": "categories.results.in_scope",
        "asylum_seeker": "categories.results.in_scope",
        "discrimination": "categories.discrimination.where",
        "antisocial": "categories.results.in_scope",
        "other": "categories.results.refer",
    }


bp.add_url_rule(
    "/housing",
    view_func=HousingLandingPage.as_view("landing", bp),
)
