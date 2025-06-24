from unittest import mock

from flask import session, views
from app.categories.constants import FAMILY
from app.categories.mixins import InScopeMixin
from app.categories.models import CategoryAnswer


class TestView(InScopeMixin, views.View):
    pass


def test_in_scope_mixin(app):
    in_scope = CategoryAnswer(
        question="This is a test question?",
        answer_value="test_answer",
        answer_label="Test answer",
        category=FAMILY.sub.family_mediation,
        question_page="categories.index",
        next_page="categories.index",
    )
    with app.app_context():
        assert TestView().dispatch_request().status_code == 302
        session.set_category_question_answer(in_scope)
        with mock.patch("flask.views.View.dispatch_request") as mock_super_dispatch_request:
            TestView().dispatch_request()
            assert mock_super_dispatch_request.called is True
