from app.categories.send import bp
from app.categories.send.forms import SendChildInCareQuestionForm
from app.categories.views import CategoryLandingPage, QuestionPage


class SendLandingPage(CategoryLandingPage):
    question_title = "Special educational needs and disability (SEND)"

    category = "send"

    routing_map = {
        "child_young_person": "categories.send.child_in_care",
        "tribunals": "categories.send.child_in_care",
        "discrimination": "categories.results.in_scope",
        "schools": "categories.results.in_scope",
        "care": "categories.community_care.landing",
        "other": "categories.results.refer",
    }


bp.add_url_rule(
    "/send/",
    view_func=SendLandingPage.as_view(
        "landing", template="categories/send/landing.html"
    ),
)
bp.add_url_rule(
    "/send/child-in-care",
    view_func=QuestionPage.as_view(
        "child_in_care",
        form_class=SendChildInCareQuestionForm,
        template="categories/question-page-caption.html",
    ),
)
bp.add_url_rule(
    "/send/age",
    view_func=QuestionPage.as_view(
        "age",
        form_class=SendAreYouUnder18Form,
        template="categories/question-page-caption.html",
    ),
)

SendLandingPage.register_routes(blueprint=bp)
