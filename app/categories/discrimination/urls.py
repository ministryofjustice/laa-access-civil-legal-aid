from . import bp
from .forms import DiscriminationWhereForm, DiscriminationWhyForm
from ..views import QuestionPage

bp.add_url_rule(
    "/discrimination/where",
    view_func=QuestionPage.as_view("where", form=DiscriminationWhereForm),
)
bp.add_url_rule(
    "/discrimination/why",
    view_func=QuestionPage.as_view("why", form=DiscriminationWhyForm),
)
