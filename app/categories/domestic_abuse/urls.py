from app.categories.domestic_abuse import bp
from app.categories.domestic_abuse.forms import WorriedAboutSomeonesSafetyForm
from app.categories.views import QuestionPage, CategoryLandingPage
from app.categories.constants import DOMESTIC_ABUSE


class DomesticAbuseLandingPage(CategoryLandingPage):
    path = "domestic-abuse"
    question_title = DOMESTIC_ABUSE.title

    category = DOMESTIC_ABUSE
    routing_map = {
        "main": [
            (
                DOMESTIC_ABUSE.sub.protect_you_and_your_children,
                "categories.domestic_abuse.are_you_at_risk_of_harm",
            ),
            (
                DOMESTIC_ABUSE.sub.leaving_an_abusive_relationship,
                "categories.domestic_abuse.are_you_at_risk_of_harm",
            ),
            (
                DOMESTIC_ABUSE.sub.problems_with_ex_partner,
                "categories.domestic_abuse.are_you_at_risk_of_harm",
            ),
        ],
        "more": [
            (
                DOMESTIC_ABUSE.sub.forced_marriage,
                "categories.domestic_abuse.are_you_at_risk_of_harm",
            ),
            (
                DOMESTIC_ABUSE.sub.fgm,
                "categories.domestic_abuse.are_you_at_risk_of_harm",
            ),
            (DOMESTIC_ABUSE.sub.problems_with_neighbours, "contact.contact_us"),
            (
                DOMESTIC_ABUSE.sub.housing_homelessness_losing_home,
                "categories.housing.landing",
            ),
        ],
        "other": "categories.results.refer",
    }


DomesticAbuseLandingPage.register_routes_2(bp)
bp.add_url_rule(
    "/domestic-abuse/are-you-at-risk-of-harm",
    view_func=QuestionPage.as_view(
        "are_you_at_risk_of_harm", form_class=WorriedAboutSomeonesSafetyForm
    ),
)
