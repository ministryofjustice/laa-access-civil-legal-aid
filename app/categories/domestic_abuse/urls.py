from app.categories.domestic_abuse import bp
from app.categories.domestic_abuse.forms import WorriedAboutSomeonesSafetyForm
from app.categories.views import QuestionPage, CategoryLandingPage
from app.categories.constants import DOMESTIC_ABUSE


class DomesticAbuseLandingPage(CategoryLandingPage):
    question_title = DOMESTIC_ABUSE.title

    category = DOMESTIC_ABUSE

    routing_map = {
        "protect_you_and_your_children": "categories.domestic_abuse.are_you_at_risk_of_harm",
        "leaving_an_abusive_relationship": "categories.domestic_abuse.are_you_at_risk_of_harm",
        "problems_with_ex_partner": "categories.domestic_abuse.are_you_at_risk_of_harm",
        "problems_with_neighbours": "contact.contact_us",
        "housing_homelessness_losing_home": "categories.housing.landing",
        "forced_marriage": "categories.domestic_abuse.are_you_at_risk_of_harm",
        "fgm": "categories.domestic_abuse.are_you_at_risk_of_harm",
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
