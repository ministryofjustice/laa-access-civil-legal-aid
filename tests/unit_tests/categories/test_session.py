from app.categories.constants import Category, HOUSING
from app.categories.models import ScopeAnswer


def test_set_category_question_answer_new_session(app, client):
    with client.session_transaction() as session:
        answer = ScopeAnswer(
            question="What is your favourite mode of transport?",
            answer_value="bus",
            answer_label="Bus",
            next_page="categories.index",
            question_page="categories.housing.landing",
            category=HOUSING,
        )
        session.set_category_question_answer(answer)

        assert "category_answers" in session
        assert session["category_answers"] == [answer]


def test_set_category_question_answer_updates_existing(app, client):
    with client.session_transaction() as session:
        answer = ScopeAnswer(
            question="What is your favourite mode of transport?",
            answer_value="bus",
            answer_label="Bus",
            next_page="categories.index",
            question_page="categories.housing.landing",
            category=HOUSING,
        )
        updated_answer = ScopeAnswer(
            question="What is your favourite mode of transport?",
            answer_value="car",
            answer_label="Car",
            next_page="categories.index",
            question_page="categories.housing.landing",
            category=HOUSING,
        )
        session["category_answers"] = [answer]
        session.set_category_question_answer(updated_answer)
        assert session["category_answers"] == [updated_answer]


def test_get_category_question_answer_empty_session(app, client):
    with client.session_transaction() as session:
        result = session.get_category_question_answer("test_question")
        assert result is None


def test_get_category_question_answer_found(app, client):
    first_answer = ScopeAnswer(
        question="What is your favourite mode of transport?",
        answer_value="bus",
        answer_label="Bus",
        next_page="categories.index",
        question_page="categories.housing.landing",
        category=HOUSING,
    )
    second_answer = ScopeAnswer(
        question="Where did this happen?",
        answer_value="home",
        answer_label="Home",
        next_page="categories.index",
        question_page="categories.housing.landing",
        category=HOUSING,
    )
    with client.session_transaction() as session:
        session["category_answers"] = [first_answer, second_answer]
        result = session.get_category_question_answer("Where did this happen?")
        assert result == "home"


def test_get_category_question_answer_not_found(app, client):
    answer = ScopeAnswer(
        question="What is your favourite mode of transport?",
        answer_value="bus",
        answer_label="Bus",
        next_page="categories.index",
        question_page="categories.housing.landing",
        category=HOUSING,
    )
    with client.session_transaction() as session:
        session["category_answers"] = [answer]
        result = session.get_category_question_answer("Hello?")
        assert result is None


def test_set_category_dataclass(app, client):
    from app.categories.constants import EDUCATION

    assert isinstance(EDUCATION, Category)

    with client.session_transaction() as session:
        session["category"] = EDUCATION
        assert session.category == EDUCATION
        assert isinstance(session.category, Category)


def test_set_category_dict(app, client):
    new_category = {
        "code": "EDUCATION",
        "title": "Education",
        "description": "This is a test",
        "chs_code": "EDUCATION",
        "article_category_name": "education",
    }

    assert isinstance(new_category, dict)

    with client.session_transaction() as session:
        session["category"] = new_category
        assert session.category == Category(**new_category)
        assert isinstance(session.category, Category)
