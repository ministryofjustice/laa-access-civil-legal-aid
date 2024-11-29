from app.session import set_category_question_answer, get_category_question_answer


def test_set_category_question_answer_new_session(mocker):
    mock_session = {}
    mocker.patch("app.session.session", mock_session)

    set_category_question_answer("Q1", "A1", "C1")

    assert "category_answers" in mock_session
    assert mock_session["category_answers"] == [
        {"question": "Q1", "answer": "A1", "category": "C1"}
    ]


def test_set_category_question_answer_updates_existing(mocker):
    mock_session = {
        "category_answers": [{"question": "Q1", "answer": "A1", "category": "C1"}]
    }
    mocker.patch("app.session.session", mock_session)

    set_category_question_answer("Q1", "A2", "C2")

    assert mock_session["category_answers"] == [
        {"question": "Q1", "answer": "A2", "category": "C2"}
    ]


def test_get_category_question_answer_empty_session(mocker):
    mock_session = {}
    mocker.patch("app.session.session", mock_session)

    result = get_category_question_answer("test_question")
    assert result is None


def test_get_category_question_answer_found(mocker):
    mock_session = {
        "category_answers": [
            {"question": "test_question", "answer": "A1", "category": "C1"}
        ]
    }
    mocker.patch("app.session.session", mock_session)

    result = get_category_question_answer("test_question")
    assert result == "A1"


def test_get_category_question_answer_not_found(mocker):
    mock_session = {
        "category_answers": [
            {"question": "other_question", "answer": "A1", "category": "C1"}
        ]
    }
    mocker.patch("app.session.session", mock_session)

    result = get_category_question_answer("test_question")
    assert result is None
