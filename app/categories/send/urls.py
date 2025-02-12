from app.categories.send import bp
from app.categories.send.forms import SendChildInCareQuestionForm
from app.categories.views import CategoryLandingPage, QuestionPage
from app.categories.constants import EDUCATION


class SendLandingPage(CategoryLandingPage):
    question_title = EDUCATION.title

    category = EDUCATION

    routing_map = {
        EDUCATION.sub.child_young_person.code: "categories.send.child_in_care",
        EDUCATION.sub.tribunals.code: "categories.send.child_in_care",
        EDUCATION.sub.discrimination.code: "categories.results.in_scope",
        EDUCATION.sub.schools.code: "categories.results.in_scope",
        EDUCATION.sub.care.code: "categories.community_care.landing",
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
    ),
)

SendLandingPage.register_routes(blueprint=bp)
