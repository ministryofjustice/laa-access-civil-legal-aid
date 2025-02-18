from app.categories.family import bp
from app.categories.views import CategoryLandingPage
from app.categories.constants import FAMILY


class FamilyLandingPage(CategoryLandingPage):
    question_title = FAMILY.title

    category = FAMILY

    routing_map = {
        "main": [
            (FAMILY.sub.social_services, "contact.contact_us"),
            (FAMILY.sub.divorce, "contact.contact_us"),
            # Todo: This needs to be updated to the onward question page when this is made
            (FAMILY.sub.domestic_abuse, "contact.contact_us"),
            (FAMILY.sub.family_mediation, "categories.results.in_scope"),
            (FAMILY.sub.child_abducted, "contact.contact_us"),
        ],
        "more": [
            # Todo: This needs to be updated to SEND landing page when this page is made
            (FAMILY.sub.send, "categories.results.in_scope"),
            (FAMILY.sub.education, "categories.results.in_scope"),
            # Todo: # This needs to be updated to safeguarding questions when this page is made
            (FAMILY.sub.forced_marriage, "categories.results.in_scope"),
        ],
        "other": "categories.results.refer",
    }


FamilyLandingPage.register_routes(bp, path="children-families-relationships")
