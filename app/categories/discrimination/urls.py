from . import bp
from .forms import (
    DiscriminationWhereForm,
    DiscriminationWhyForm,
    DiscriminationAreYouUnder18Form,
)
from ..views import QuestionPage

bp.add_url_rule(
    "/discrimination/where",
    view_func=QuestionPage.as_view("where", form_class=DiscriminationWhereForm),
)
bp.add_url_rule(
    "/discrimination/why",
    view_func=QuestionPage.as_view("why", form_class=DiscriminationWhyForm),
)
bp.add_url_rule(
    "/discrimination/age",
    view_func=QuestionPage.as_view(
        "age",
        form_class=DiscriminationAreYouUnder18Form,
    ),
)
