from app.categories.public import bp
from app.categories.views import CategoryLandingPage, QuestionPage
from app.categories.public.forms import PolicePrisonOrDetentionCentreForm
from app.categories.constants import PUBLIC_LAW


class PublicLandingPage(CategoryLandingPage):
    question_title = "Legal action against police and public organisations"
    category = PUBLIC_LAW


bp.add_url_rule(
    "/public",
    view_func=PublicLandingPage.as_view(
        "landing", template="categories/public/landing.html"
    ),
)

bp.add_url_rule(
    "/public/reason",
    view_func=QuestionPage.as_view(
        "reason",
        form_class=PolicePrisonOrDetentionCentreForm,
    ),
)
