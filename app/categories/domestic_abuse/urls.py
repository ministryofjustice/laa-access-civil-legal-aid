from app.categories.domestic_abuse import bp
from app.categories.domestic_abuse.forms import AreYouAtRiskOfHarmForm
from app.categories.views import QuestionPage, CategoryLandingPage


class DomesticAbuseLandingPage(CategoryLandingPage):
    template = "categories/domestic-abuse.html"

    question_title = "Domestic Abuse"

    category = "Domestic Abuse"

    routing_map = {
        "protect_you_and_your_children": "categories.domestic_abuse.are_you_at_risk_of_harm",
    }


bp.add_url_rule(
    "/domestic-abuse/",
    view_func=DomesticAbuseLandingPage.as_view("landing", bp),
)
bp.add_url_rule(
    "/domestic-abuse/are-you-at-risk-of-harm",
    view_func=QuestionPage.as_view(
        "are_you_at_risk_of_harm", form_class=AreYouAtRiskOfHarmForm
    ),
)
