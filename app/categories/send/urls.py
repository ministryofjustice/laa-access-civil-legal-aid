from app.categories.send import bp
from app.categories.send.forms import SendChildInCareQuestionForm
from app.categories.views import CategoryLandingPage, QuestionPage
from app.categories.constants import EDUCATION


class SendLandingPage(CategoryLandingPage):
    question_title = EDUCATION.title

    category = EDUCATION

    routing_map = {
        "main": [
            (EDUCATION.sub.child_young_person, "categories.send.child_in_care"),
            (EDUCATION.sub.tribunals, "categories.send.child_in_care"),
            (EDUCATION.sub.discrimination, "categories.results.in_scope"),
        ],
        "more": [
            (EDUCATION.sub.schools, "categories.results.in_scope"),
            (EDUCATION.sub.care, "categories.community_care.landing"),
        ],
        "other": "categories.results.refer",
    }


SendLandingPage.register_routes(blueprint=bp, path="send")
bp.add_url_rule(
    "/send/child-in-care",
    view_func=QuestionPage.as_view(
        "child_in_care",
        form_class=SendChildInCareQuestionForm,
    ),
)
