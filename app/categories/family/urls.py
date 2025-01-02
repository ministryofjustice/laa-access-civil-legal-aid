from app.categories.family import bp
from app.categories.views import CategoryLandingPage
from app.categories.categories import Category


class FamilyLandingPage(CategoryLandingPage):
    question_title = "Children, families, and relationships"

    category = Category.FAMILY

    routing_map = {
        "social_services": "contact.contact_us",
        "divorce": "contact.contact_us",
        "domestic_abuse": "contact.contact_us",  # This needs to be updated to the onward question page when this is made
        "family_mediation": "categories.results.in_scope",
        "child_abducted": "contact.contact_us",
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
