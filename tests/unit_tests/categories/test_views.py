from flask import session
from wtforms import RadioField
from wtforms.validators import InputRequired
from app.categories.widgets import CategoryRadioInput
from app.categories.family.urls import FamilyLandingPage, FAMILY
from app.categories.views import QuestionPage, QuestionForm


def test_category_page_dispatch(app):
    with app.app_context():
        page = FamilyLandingPage(
            route_endpoint="family", template=FamilyLandingPage.template
        )
        page.dispatch_request()
        assert session.category == FamilyLandingPage.category


def test_question_page_next_page(app):
    class TestQuestionForm(QuestionForm):
        next_step_mapping = {
            "yes": "categories.results.in_scope",
            "no": "categories.results.refer",
            "notsure": "categories.index",
            "fala": {
                "endpoint": "find-a-legal-adviser.search",
                "category": "mhe",
                "secondary_category": "com",
            },
        }
        question = RadioField(
            "This is a test question?",
            widget=CategoryRadioInput(
                show_divider=False
            ),  # Uses our override class to support setting custom CSS on the label title
            validators=[InputRequired(message="Validation failed message")],
            choices=[
                ("yes", "Yes"),
                ("no", "No"),
            ],
        )

    with app.app_context():
        form = TestQuestionForm(category=FAMILY, question="yes")
        view = QuestionPage(form_class=form)
        assert "/legal-aid-available" == view.get_next_page("yes")

        form = TestQuestionForm(category=FAMILY, question="no")
        view = QuestionPage(form_class=form)
        assert "/refer" == view.get_next_page("no")

        form = TestQuestionForm(category=FAMILY, question="notsure")
        view = QuestionPage(form_class=form)
        assert "/" == view.get_next_page("notsure")

        form = TestQuestionForm(category=FAMILY, question="notsure")
        view = QuestionPage(form_class=form)
        assert (
            "/find-a-legal-adviser?category=mhe&secondary_category=com"
            == view.get_next_page("fala")
        )
