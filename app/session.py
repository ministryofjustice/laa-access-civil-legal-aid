from flask import session


def set_category_question_answer(question: str, answer: str, category: str) -> None:
    """Store a question-answer pair with the question category in the session.

    Args:
        question: The question text
        answer: The answer text
        category: The category name

    Side effects:
        Updates session['category_answers'] list
    """
    if "category_answers" not in session:
        session["category_answers"] = []

    answers: list[dict[str, str]] = session["category_answers"]

    # Remove existing entry if present
    answers = [entry for entry in answers if entry["question"] != question]

    answers.append({"question": question, "answer": answer, "category": category})

    session["category_answers"] = answers


def get_category_question_answer(question_title: str) -> str | None:
    """Retrieve an answer for a question from the session.

    Args:
        question_title: The title of the question to look up

    Returns:
        The stored answer string if found, None otherwise
    """
    if "category_answers" not in session:
        return None

    answers: list[dict[str, str]] = session["category_answers"]

    for answer in answers:
        if answer["question"] == question_title:
            return answer["answer"]
    return None
