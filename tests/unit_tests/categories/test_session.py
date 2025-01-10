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
