from unittest.mock import patch
import pytest
from flask import session
from wtforms.fields.choices import RadioField

from app.categories.family.urls import FamilyLandingPage
from app.categories.forms import QuestionForm
from app.categories.views import QuestionPage


def test_category_page_dispatch(app):
    with app.app_context():
        page = FamilyLandingPage(FamilyLandingPage.template)
        page.dispatch_request()
        assert session.category == FamilyLandingPage.category


class MockQuestionForm(QuestionForm):
    category = "test_category"
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
    assert question_page.category == "test_category"


def test_initialization_custom_template():
    custom_template = "custom/template.html"
    page = QuestionPage(MockQuestionForm, template=custom_template)
    assert page.template == custom_template


def test_get_next_page_single_answer(mock_url_for, app, client, question_page):
    """Test get_next_page with single straightforward answer"""
    with app.test_request_context():
        next_page = question_page.get_next_page("yes")
        mock_url_for.assert_called_once_with("next_page_yes")
        assert next_page.location == "/mocked/next_page_yes"


def test_get_next_page_optional_answer(mock_url_for, app, client, question_page):
    """Test get_next_page with optional answers"""
    with app.test_request_context():
        next_page = question_page.get_next_page(["notsure"])
        mock_url_for.assert_called_once_with("next_page_notsure")
        assert next_page.location == "/mocked/next_page_notsure"


def test_get_next_page_multiple_answers(mock_url_for, app, client, question_page):
    """Test get_next_page with multiple answers"""
    with app.test_request_context():
        next_page = question_page.get_next_page(["yes", "no"])
        mock_url_for.assert_called_once_with("next_page_yes")
        assert next_page.location == "/mocked/next_page_yes"


def test_get_next_page_dict_route(mock_url_for, app, client, question_page):
    """Test get_next_page with dictionary routing configuration"""
    with app.test_request_context():
        next_page = question_page.get_next_page("dict_route")
        mock_url_for.assert_called_once_with(endpoint="custom_page", param="value")
        assert next_page.location == "/mocked/custom_page"


def test_get_next_page_catch_all(mock_url_for, app, client, question_page):
    """Test get_next_page with catch-all route"""
    with app.test_request_context():
        next_page = question_page.get_next_page(["unknown1", "unknown2"])
        mock_url_for.assert_called_once_with("catch_all_page")
        assert next_page.location == "/mocked/catch_all_page"


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
            assert isinstance(
                mock_render_template.mock_calls[0].kwargs["form"], MockQuestionForm
            )

    def test_process_request_on_valid_submit(self, app, client, question_page):
        with app.test_request_context(
            "/fake-url", method="POST", data={"question": "yes", "submit": "y"}
        ):
            with (
                patch.object(question_page, "get_next_page") as mock_get_next_page,
                patch.object(question_page, "update_session") as mock_update_session,
            ):
                question_page.process_request()
                mock_get_next_page.assert_called_once_with("yes")
                mock_update_session.assert_called_once_with(
                    question="test_question", answer="yes", category="test_category"
                )

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
