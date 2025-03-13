from flask import session
from app.categories.constants import FAMILY
from app.categories.mixins import InScopeMixin
from app.categories.models import CategoryAnswer


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
        assert InScopeMixin().ensure_in_scope().status_code == 302
        session.set_category_question_answer(in_scope)
        assert InScopeMixin().ensure_in_scope() is None
