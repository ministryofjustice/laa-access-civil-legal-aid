from app.categories.domestic_abuse import bp
from app.categories.domestic_abuse.forms import AreYouAtRiskOfHarmForm
from app.categories.views import QuestionPage, CategoryLandingPage

bp.add_url_rule(
    "/domestic-abuse/",
    view_func=CategoryLandingPage.as_view("landing", "categories/domestic-abuse.html"),
)
bp.add_url_rule(
    "/domestic-abuse/are-you-at-risk-of-harm",
    view_func=QuestionPage.as_view(
        "are_you_at_risk_of_harm", form_class=AreYouAtRiskOfHarmForm
    ),
)
