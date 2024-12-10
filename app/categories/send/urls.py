from app.categories.send import bp
from app.categories.views import CategoryLandingPage


class SendLandingPage(CategoryLandingPage):
    question_title = "Special educational needs and disability (SEND)"

    category = "send"

    routing_map = {
        "child_young_person": "categories.index",
        "tribunals": "categories.index",
        "child_in_care": "categories.index",
        "discrimination": "categories.results.in_scope",
        "schools": "categories.results.in_scope",
        "disability": "categories.index",
        "other": "categories.results.refer",
    }


bp.add_url_rule(
    "/send/",
    view_func=SendLandingPage.as_view(
        "landing", template="categories/send/landing.html"
    ),
)

SendLandingPage.register_routes(blueprint=bp)
