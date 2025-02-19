from app.categories.constants import Category


def test_set_category_question_answer_new_session(app, client):
    with client.session_transaction() as session:
        session.set_category_question_answer("Q1", "A1", "C1")

        assert "category_answers" in session
        assert session["category_answers"] == [
            {"question": "Q1", "answer": "A1", "category": "C1"}
        ]


def test_set_category_question_answer_updates_existing(app, client):
    with client.session_transaction() as session:
        session["category_answers"] = [
            {"question": "Q1", "answer": "A1", "category": "C1"}
        ]
        session.set_category_question_answer("Q1", "A2", "C2")
        assert session["category_answers"] == [
            {"question": "Q1", "answer": "A2", "category": "C2"}
        ]


def test_get_category_question_answer_empty_session(app, client):
    with client.session_transaction() as session:
        result = session.get_category_question_answer("test_question")
        assert result is None


def test_get_category_question_answer_found(app, client):
    with client.session_transaction() as session:
        session["category_answers"] = [
            {"question": "test_question", "answer": "A1", "category": "C1"}
        ]
        result = session.get_category_question_answer("test_question")
        assert result == "A1"


def test_get_category_question_answer_not_found(app, client):
    with client.session_transaction() as session:
        session["category_answers"] = [
            {"question": "other_question", "answer": "A1", "category": "C1"}
        ]
        result = session.get_category_question_answer("test_question")
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
