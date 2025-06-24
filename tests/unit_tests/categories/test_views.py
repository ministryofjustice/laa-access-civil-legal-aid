import pytest
from flask import session
from app.categories.family.urls import FamilyLandingPage
from unittest.mock import Mock, patch
from app.categories.constants import FAMILY
from app.categories.results.views import (
    OutOfScopePage,
    CannotFindYourProblemPage,
    NextStepsPage,
)
from wtforms import RadioField, StringField, IntegerField
from wtforms.validators import InputRequired
from app.categories.widgets import CategoryRadioInput
from app.categories.views import QuestionPage, QuestionForm


def test_category_page_dispatch(app):
    with app.app_context():
        page = FamilyLandingPage(route_endpoint="family", template=FamilyLandingPage.template)
        page.dispatch_request()
        assert session.category == FamilyLandingPage.category


class MockQuestionForm(QuestionForm):
    category = FAMILY
    title = "test_question"
    next_step_mapping = {
        "yes": "next_page_yes",
        "no": "next_page_no",
        "notsure": "next_page_notsure",
        "none": "next_page_none",
        "*": "catch_all_page",
        "dict_route": {"endpoint": "custom_page", "param": "value"},
    }

    question = RadioField(
        "Question",
        choices=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
    )

    @property
    def csrf_token(self):
        def generate_csrf_token():
            return "fake-csrf-token"

        return generate_csrf_token


@pytest.fixture
def question_page():
    page = QuestionPage(MockQuestionForm)
    return page


def test_initialization(question_page):
    assert question_page.form_class == MockQuestionForm
    assert question_page.template == "categories/question-page.html"
    assert question_page.category == FAMILY


def test_initialization_custom_template():
    custom_template = "custom/template.html"
    page = QuestionPage(MockQuestionForm, template=custom_template)
    assert page.template == custom_template


def test_get_next_page_single_answer(mock_url_for, app, client, question_page):
    """Test get_next_page with single straightforward answer"""
    with app.test_request_context():
        next_page = question_page.get_next_page("yes")
        mock_url_for.assert_called_once_with("next_page_yes")
        assert next_page == "/mocked/next_page_yes"


def test_get_next_page_optional_answer(mock_url_for, app, client, question_page):
    """Test get_next_page with optional answers"""
    with app.test_request_context():
        next_page = question_page.get_next_page(["notsure"])
        mock_url_for.assert_called_once_with("next_page_notsure")
        assert next_page == "/mocked/next_page_notsure"


def test_get_next_page_multiple_answers(mock_url_for, app, client, question_page):
    """Test get_next_page with multiple answers"""
    with app.test_request_context():
        next_page = question_page.get_next_page(["yes", "no"])
        mock_url_for.assert_called_once_with("next_page_yes")
        assert next_page == "/mocked/next_page_yes"


def test_get_next_page_dict_route(mock_url_for, app, client, question_page):
    """Test get_next_page with dictionary routing configuration"""
    with app.test_request_context():
        next_page = question_page.get_next_page("dict_route")
        mock_url_for.assert_called_once_with(endpoint="custom_page", param="value")
        assert next_page == "/mocked/custom_page"


def test_get_next_page_catch_all(mock_url_for, app, client, question_page):
    """Test get_next_page with catch-all route"""
    with app.test_request_context():
        next_page = question_page.get_next_page(["unknown1", "unknown2"])
        mock_url_for.assert_called_once_with("catch_all_page")
        assert next_page == "/mocked/catch_all_page"


def test_get_next_page_invalid_answer(app, client, question_page):
    """Test get_next_page with invalid answer, wildcard routing is only used if the answer is a list"""
    with app.test_request_context():
        with pytest.raises(ValueError) as exc_info:
            question_page.get_next_page("invalid_answer")
        assert "No mapping found for answer" in str(exc_info.value)


class TestProcessRequest:
    def test_process_request_form(self, app, client, question_page):
        with patch("app.categories.views.render_template") as mock_render_template:
            question_page.process_request()
            assert isinstance(mock_render_template.mock_calls[0].kwargs["form"], MockQuestionForm)

    def test_process_request_on_valid_submit(self, app, client, question_page):
        with app.test_request_context("/fake-url", method="POST", data={"question": "yes", "submit": "y"}):
            with (
                patch.object(question_page, "get_next_page") as mock_get_next_page,
                patch.object(question_page, "update_session") as mock_update_session,
            ):
                question_page.process_request()
                mock_get_next_page.assert_called_once_with("yes")
                mock_update_session.assert_called_once()
                assert isinstance(mock_update_session.mock_calls[0].args[0], MockQuestionForm)

    def test_clear_session_if_called_with_errors(self, app, client, question_page):
        with app.test_request_context(
            "/fake-url",
            method="POST",
            data={"question": "invalid_answer", "submit": "y"},
        ):
            with patch(
                "app.categories.views.session.remove_category_question_answer"
            ) as mock_remove_answer_from_session:
                question_page.process_request()
                mock_remove_answer_from_session.assert_called()


class TestOutOfScopePage:
    def test_init(self):
        page = OutOfScopePage("test.html", category=FAMILY)
        assert page.template == "test.html"
        assert page.category == FAMILY

    def test_dispatch_request(self, app):
        with app.test_request_context("/"):
            page = OutOfScopePage("test.html", category=FAMILY)

            # Mock get_context method
            expected_context = {"test_key": "test_value"}
            page.get_context = Mock(return_value=expected_context)


class TestCannotFindYourProblemPage:
    def test_init_default_next_steps(self):
        page = CannotFindYourProblemPage()
        assert page.template == "categories/cannot-find-problem.html"
        assert page.next_steps_page == "categories.results.next_steps"
        assert page.get_help_organisations is False

    def test_init_custom_next_steps(self):
        custom_next_steps = "custom.next.steps"
        page = CannotFindYourProblemPage(next_steps_page=custom_next_steps)
        assert page.next_steps_page == custom_next_steps

    def test_get_context(self):
        page = CannotFindYourProblemPage()

        parent_context = {"parent_key": "parent_value"}
        with patch.object(OutOfScopePage, "get_context", return_value=parent_context):
            context = page.get_context(FAMILY)

            assert context["parent_key"] == "parent_value"
            assert context["next_steps_page"] == page.next_steps_page


class TestNextStepsPage:
    def test_init(self):
        page = NextStepsPage()
        assert page.template == "categories/next-steps-alternate-help.html"

    def test_init_with_category(self):
        page = NextStepsPage(category=FAMILY)
        assert page.template == "categories/next-steps-alternate-help.html"
        assert page.category == FAMILY

    def test_init_with_no_help_organisations(self):
        page = NextStepsPage(get_help_organisations=False)
        assert page.template == "categories/next-steps.html"


def test_question_page_next_page(app):
    class TestQuestionForm(QuestionForm):
        next_step_mapping = {
            "yes": "categories.results.in_scope",
            "no": "categories.results.cannot_find_your_problem",
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
        assert "/cannot-find-your-problem" == view.get_next_page("no")

        form = TestQuestionForm(category=FAMILY, question="notsure")
        view = QuestionPage(form_class=form)
        assert "/find-your-problem" == view.get_next_page("notsure")

        form = TestQuestionForm(category=FAMILY, question="notsure")
        view = QuestionPage(form_class=form)
        assert "/find-a-legal-adviser?category=mhe&secondary_category=com" == view.get_next_page("fala")


def test_question_page_enforce_dependency(app):
    class TestQuestion1(QuestionForm):
        category = FAMILY
        title = "What is your name?"
        name = StringField("")

    class TestQuestion2(QuestionForm):
        category = FAMILY
        depends_on = TestQuestion1
        title = "How old are you?"
        age = IntegerField()

    values = {}

    def mock_session_get_category_question_answer(question_title):
        return values.get(question_title, None)

    view = QuestionPage(form_class=TestQuestion2)
    with app.app_context():
        with patch.object(
            session,
            "get_category_question_answer",
            side_effect=mock_session_get_category_question_answer,
        ):
            response = view.ensure_form_dependency(view.form_class())
            assert response.status_code == 302
            values[TestQuestion1.title] = "John Doe"
            response = view.ensure_form_dependency(view.form_class())
            assert response is None
