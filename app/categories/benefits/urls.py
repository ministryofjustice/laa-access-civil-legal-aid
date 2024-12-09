from . import bp
from .forms import AppealQuestionForm
from ..views import QuestionPage

bp.add_url_rule(
    "/benefits/appeal",
    view_func=QuestionPage.as_view(
        "appeal",
        form_class=AppealQuestionForm,
        template="categories/benefits/appeal.html",
    ),
)
