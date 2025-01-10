from flask.sessions import SecureCookieSession, SecureCookieSessionInterface
from app.categories.constants import Category


class Session(SecureCookieSession):
    @property
    def category_obj(self) -> Category | None:
        """Get the category from the session.

        Returns:
            The category name if found, None otherwise
        """
        return Category(**self.get("category"))

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


class SessionInterface(SecureCookieSessionInterface):
    session_class = Session
