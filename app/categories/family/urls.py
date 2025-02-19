from app.categories.family import bp
from app.categories.results.views import NextStepsPage, CannotFindYourProblemPage
from app.categories.views import CategoryLandingPage
from app.categories.constants import FAMILY


class FamilyLandingPage(CategoryLandingPage):
    question_title = FAMILY.title

    category = FAMILY

    routing_map = {
        "main": [
            (FAMILY.sub.social_services, "contact.contact_us"),
            (FAMILY.sub.divorce, "contact.contact_us"),
            (
                FAMILY.sub.domestic_abuse,
                "categories.domestic_abuse.are_you_at_risk_of_harm",
            ),
            (FAMILY.sub.family_mediation, "categories.results.in_scope"),
            (FAMILY.sub.child_abducted, "means_test.eligible"),
        ],
        "more": [
            (FAMILY.sub.send, "categories.send.landing"),
            (FAMILY.sub.education, "categories.results.in_scope"),
            (
                FAMILY.sub.forced_marriage,
                "categories.domestic_abuse.are_you_at_risk_of_harm",
            ),
        ],
        "other": "categories.family.cannot_find_your_problem",
    }


FamilyLandingPage.register_routes(bp, path="children-families-relationships")
bp.add_url_rule(
    "/children-families-relationships/cannot-find-your-problem",
    view_func=CannotFindYourProblemPage.as_view(
        "cannot_find_your_problem",
        next_steps_page="categories.family.next_steps",
    ),
)
bp.add_url_rule(
    "/children-families-relationships/next-steps",
    view_func=NextStepsPage.as_view(
        "next_steps",
        category=FAMILY,
    ),
)
