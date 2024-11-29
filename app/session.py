from flask import session

from app.categories.forms import QuestionForm


def set_category_question_answer(question: str, answer: str, category: str):
    if "category_answers" not in session:
        session["category_answers"] = []

    for entry in session["category_answers"]:
        if entry["question"] == question:
            session["category_answers"].remove(entry)

    session["category_answers"].append(
        {"question": question, "answer": answer, "category": category}
    )


def get_category_question_answer(question_form: QuestionForm):
    if "category_answers" not in session:
        return None
    for answer in session["category_answers"]:
        if answer["question"] == question_form.title:
            return answer["answer"]
    return None
