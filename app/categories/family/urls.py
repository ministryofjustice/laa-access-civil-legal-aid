from app.categories.family import bp
from app.categories.views import CategoryLandingPage
from app.categories.constants import FAMILY


class FamilyLandingPage(CategoryLandingPage):
    question_title = FAMILY.title

    category = FAMILY

    routing_map = {
        FAMILY.sub.social_services.code: "contact.contact_us",
        FAMILY.sub.divorce.code: "contact.contact_us",
        FAMILY.sub.domestic_abuse.code: "contact.contact_us",  # This needs to be updated to the onward question page when this is made
        FAMILY.sub.family_mediation.code: "categories.results.in_scope",
        FAMILY.sub.child_abducted.code: "contact.contact_us",
        FAMILY.sub.send.code: "categories.results.in_scope",  # This needs to be updated to SEND landing page when this page is made
        FAMILY.sub.education.code: "categories.results.in_scope",
        FAMILY.sub.forced_marriage.code: "categories.results.in_scope",  # This needs to be updated to safeguarding questions when this page is made
        "other": "categories.results.refer",
    }


bp.add_url_rule(
    "/children-families-relationships/",
    view_func=FamilyLandingPage.as_view(
        "landing", template="categories/family/landing.html"
    ),
)
FamilyLandingPage.register_routes(bp)
