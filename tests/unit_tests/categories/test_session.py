import pytest
from flask import url_for

from app.categories.constants import Category, HOUSING
from app.categories.models import CategoryAnswer, QuestionType


def test_set_category_question_answer_new_session(app, client):
    with client.session_transaction() as session:
        answer = CategoryAnswer(
            question="What is your favourite mode of transport?",
            answer_value="bus",
            answer_label="Bus",
            next_page="categories.index",
            question_page="categories.housing.landing",
            category=HOUSING,
        )
        session.set_category_question_answer(answer)

        assert "category_answers" in session
        expected_category_answers = [answer.__dict__]
        expected_category_answers[0]["category"] = {"code": "housing"}
        assert session["category_answers"] == expected_category_answers


def test_set_category_question_answer_updates_existing(app, client):
    with client.session_transaction() as session:
        answer = CategoryAnswer(
            question="What is your favourite mode of transport?",
            answer_value="bus",
            answer_label="Bus",
            next_page="categories.index",
            question_page="categories.housing.landing",
            category=HOUSING,
        )
        session.set_category_question_answer(answer)
        updated_answer = CategoryAnswer(
            question="What is your favourite mode of transport?",
            answer_value="car",
            answer_label="Car",
            next_page="categories.index",
            question_page="categories.housing.landing",
            category=HOUSING,
        )
        session.set_category_question_answer(updated_answer)
        expected_category_answers = [updated_answer.__dict__]
        expected_category_answers[0]["category"] = {"code": "housing"}
        assert session["category_answers"] == expected_category_answers


def test_get_category_question_answer_empty_session(app, client):
    with client.session_transaction() as session:
        result = session.get_category_question_answer("test_question")
        assert result is None


def test_get_category_question_answer_found(app, client):
    first_answer = CategoryAnswer(
        question="What is your favourite mode of transport?",
        answer_value="bus",
        answer_label="Bus",
        next_page="categories.index",
        question_page="categories.housing.landing",
        category=HOUSING,
    )
    second_answer = CategoryAnswer(
        question="Where did this happen?",
        answer_value="home",
        answer_label="Home",
        next_page="categories.index",
        question_page="categories.housing.landing",
        category=HOUSING,
    )
    with client.session_transaction() as session:
        session.set_category_question_answer(first_answer)
        session.set_category_question_answer(second_answer)
        result = session.get_category_question_answer("Where did this happen?")
        assert result == "home"


def test_get_category_question_answer_not_found(app, client):
    answer = CategoryAnswer(
        question="What is your favourite mode of transport?",
        answer_value="bus",
        answer_label="Bus",
        next_page="categories.index",
        question_page="categories.housing.landing",
        category=HOUSING,
    )
    with client.session_transaction() as session:
        session.set_category_question_answer(answer)
        result = session.get_category_question_answer("Hello?")
        assert result is None


def test_set_category_dataclass(app, client):
    from app.categories.constants import EDUCATION

    assert isinstance(EDUCATION, Category)

    with client.session_transaction() as session:
        session["category"] = {"code": EDUCATION.code}
        assert session.category == EDUCATION
        assert isinstance(session.category, Category)


class TestPrimaryCategoryAnswer:
    @pytest.mark.parametrize(
        "category",
        [
            "housing",
            "discrimination",
            "family",
            "send",
        ],
    )
    def test_set_category(self, category, app, client):
        client.get(url_for(f"categories.{category}.landing"))

        with client.session_transaction() as session:
            assert len(session.category_answers) == 1
            category_answer = session.category_answers[0]
            assert category_answer.question == "Choose the problem you need help with."
            assert category_answer.answer_value == category
            assert isinstance(category_answer, CategoryAnswer)


class TestSessionSubcategory:
    def test_subcategory_none_when_no_answers(self, app, client):
        with client.session_transaction() as session:
            session["category_answers"] = []

        assert session.subcategory is None

    def test_subcategory_returns_category_when_found(self, app, client):
        with client.session_transaction() as session:
            session["category_answers"] = [
                {
                    "question": "Housing, homelessness, losing your home",
                    "answer_value": "homelessness",
                    "answer_label": "Homelessness",
                    "category": {"code": "homelessness", "parent_code": "housing"},
                    "question_page": "categories.housing.landing",
                    "next_page": "categories.results.in_scope_hlpas",
                    "question_type": QuestionType.SUB_CATEGORY,
                }
            ]

        result = session.subcategory

        assert result.code == "homelessness"

    def test_subcategory_ignores_non_subcategory_answers(self, client):
        with client.session_transaction() as session:
            session["category_answers"] = [
                {
                    "question": "Choose the problem you need help with.",
                    "question_page": "categories.index",
                    "answer_value": "housing",
                    "answer_label": "Housing, homelessness, losing your home",
                    "category": {"code": "housing"},
                    "question_type": QuestionType.CATEGORY,
                    "next_page": "categories.housing.landing",
                }
            ]

        result = session.subcategory

        assert result is None

    def test_subcategory_raises_error_for_multiple_subcategories(self, client):
        with client.session_transaction() as session:
            session["category_answers"] = [
                {
                    "question": "Housing, homelessness, losing your home",
                    "answer_value": "homelessness",
                    "answer_label": "Homelessness",
                    "category": {"code": "homelessness", "parent_code": "housing"},
                    "question_page": "categories.housing.landing",
                    "next_page": "categories.results.in_scope_hlpas",
                    "question_type": QuestionType.SUB_CATEGORY,
                },
                {
                    "question": "Housing, homelessness, losing your home",
                    "answer_value": "eviction",
                    "answer_label": "Eviction, told to leave your home",
                    "category": {"code": "eviction", "parent_code": "housing"},
                    "question_page": "categories.housing.landing",
                    "next_page": "categories.results.in_scope_hlpas",
                    "question_type": QuestionType.SUB_CATEGORY,
                },
            ]

        with pytest.raises(ValueError) as e:
            _ = session.subcategory
            assert "User has multiple subcategory answers" in str(e.value)


class TestRemoveCategoryQuestionAnswer:
    def test_simple_case(self, app, client):
        with client.session_transaction() as session:
            session["category_answers"] = [
                {
                    "question": "test_question",
                    "answer": "test_answer",
                    "category": "test_category",
                }
            ]
            assert len(session["category_answers"]) == 1
            session.remove_category_question_answer("test_question")
            assert len(session["category_answers"]) == 0
            assert session["category_answers"] == []

    def test_multiple_answers(self, app, client):
        with client.session_transaction() as session:
            session["category_answers"] = [
                {"question": "Q1", "answer": "A1", "category": "C1"},
                {"question": "Q2", "answer": "A1", "category": "C1"},
                {"question": "Q3", "answer": "A1", "category": "C3"},
            ]
            assert len(session["category_answers"]) == 3
            session.remove_category_question_answer("Q2")
            assert len(session["category_answers"]) == 2
            assert session["category_answers"] == [
                {"question": "Q1", "answer": "A1", "category": "C1"},
                {"question": "Q3", "answer": "A1", "category": "C3"},
            ]
