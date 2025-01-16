from flask.sessions import SecureCookieSession, SecureCookieSessionInterface
from app.categories.constants import Category
from flask import session, current_app
from dataclasses import dataclass
from datetime import timedelta, datetime, timezone


@dataclass
class Eligibility:
    forms = {}

    def add(self, form_name, data):
        self.forms[form_name] = data

    @property
    def category(self):
        return session.get("category", {}).get("chs_code")


class Session(SecureCookieSession):
    SESSION_TIMEOUT = timedelta(minutes=30)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["eligibility"] = Eligibility()

    def update_eligibility(self, form_name, form_data):
        self["eligibility"].add(form_name, form_data)

    def get_eligibility(self):
        return self["eligibility"]

    @property
    def category(self) -> Category | None:
        """Get the category from the session.

        Returns:
            The category name if found, None otherwise
        """
        category_dict = self.get("category")
        if category_dict is None:
            return None
        return Category(**category_dict)

    @property
    def has_children(self):
        # Todo: Needs implementation
        return True

    @property
    def has_dependants(self):
        # Todo: Needs implementation
        return True

    def set_category_question_answer(
        self, question_title: str, answer: str, category: Category
    ) -> None:
        """Store a question-answer pair with the question category in the session.

        Args:
            question_title: The question text
            answer: The answer text
            category: The category name

        Side effects:
            Updates session['category_answers'] list
        """
        if "category_answers" not in self:
            self["category_answers"] = []

        answers: list[dict[str, str]] = self["category_answers"]

        # Remove existing entry if present
        answers = [entry for entry in answers if entry["question"] != question_title]

        answers.append(
            {"question": question_title, "answer": answer, "category": category}
        )

        self["category_answers"] = answers
        self["category"] = (
            category  # Update the category based on the question the user last answered
        )

    def get_category_question_answer(self, question_title: str) -> str | None:
        """Retrieve an answer for a question from the session.

        Args:
            question_title: The title of the question to look up

        Returns:
            The stored answer string if found, None otherwise
        """
        if "category_answers" not in self:
            return None

        answers: list[dict[str, str]] = self["category_answers"]

        for answer in answers:
            if answer["question"] == question_title:
                return answer["answer"]
        return None

    def update_last_active(self):
        """Update the last_active time in the session."""
        session["last_active"] = datetime.now(timezone.utc)

    def check_session_expiration(self):
        """Check if the session has expired based on inactivity."""
        if "last_active" in session:
            last_active = session["last_active"]
            current_time = datetime.now(timezone.utc)

            time_diff = current_time - last_active
            if time_diff > current_app.config["SESSION_TIMEOUT"]:
                session.clear()  # Expire the session
                return True  # Indicate the session expired

        self.update_last_active()
        return False


class SessionInterface(SecureCookieSessionInterface):
    session_class = Session
