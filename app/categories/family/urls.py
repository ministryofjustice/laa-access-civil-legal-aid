from app.categories.family import bp
from app.categories.views import CategoryLandingPage


class FamilyLandingPage(CategoryLandingPage):
    question_title = "Children, families, and relationships"

    category = "Family"

    routing_map = {
        "social_services": "categories.results.contact",
        "divorce": "categories.results.contact",
        "domestic_abuse": "categories.results.contact",  # This needs to be updated to the onward question page when this is made
        "family_mediation": "categories.results.in_scope",
        "child_abducted": "categories.results.contact",
        "send": "categories.results.in_scope",  # This needs to be updated to SEND landing page when this page is made
        "education": "categories.results.in_scope",
        "forced_marriage": "categories.results.in_scope",  # This needs to be updated to safeguarding questions when this page is made
        "other": "categories.results.refer",
    }


bp.add_url_rule(
    "/children-families-relationships/",
    view_func=FamilyLandingPage.as_view(
        "landing", template="categories/family/landing.html"
    ),
)
FamilyLandingPage.register_routes(bp)
