from app.categories.domestic_abuse import bp
from app.categories.domestic_abuse.forms import WorriedAboutSomeonesSafetyForm
from app.categories.views import QuestionPage, CategoryLandingPage
from app.categories.constants import DOMESTIC_ABUSE


class DomesticAbuseLandingPage(CategoryLandingPage):
    question_title = DOMESTIC_ABUSE.title

    category = DOMESTIC_ABUSE

    routing_map = {
        DOMESTIC_ABUSE.sub.protect_you_and_your_children.code: "categories.domestic_abuse.are_you_at_risk_of_harm",
        DOMESTIC_ABUSE.sub.leaving_an_abusive_relationship.code: "categories.domestic_abuse.are_you_at_risk_of_harm",
        DOMESTIC_ABUSE.sub.problems_with_ex_partner.code: "categories.domestic_abuse.are_you_at_risk_of_harm",
        DOMESTIC_ABUSE.sub.problems_with_neighbours.code: "contact.contact_us",
        DOMESTIC_ABUSE.sub.housing_homelessness_losing_home.code: "categories.housing.landing",
        DOMESTIC_ABUSE.sub.forced_marriage.code: "categories.domestic_abuse.are_you_at_risk_of_harm",
        DOMESTIC_ABUSE.sub.fgm.code: "categories.domestic_abuse.are_you_at_risk_of_harm",
        "other": "categories.results.refer",
    }


bp.add_url_rule(
    "/domestic-abuse/",
    view_func=DomesticAbuseLandingPage.as_view(
        "landing", template="categories/domestic_abuse/landing.html"
    ),
)
bp.add_url_rule(
    "/domestic-abuse/are-you-at-risk-of-harm",
    view_func=QuestionPage.as_view(
        "are_you_at_risk_of_harm", form_class=WorriedAboutSomeonesSafetyForm
    ),
)

DomesticAbuseLandingPage.register_routes(bp)
