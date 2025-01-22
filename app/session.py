from flask.sessions import SecureCookieSession, SecureCookieSessionInterface
from app.categories.constants import Category
from flask import session
from dataclasses import dataclass
from datetime import timedelta


@dataclass
class Eligibility:
    forms: dict[str, dict]

    def add(self, form_name, data):
        self.forms[form_name] = data

    @property
    def category(self):
        return session.get("category", {}).get("chs_code")

    def is_yes(self, form_name, field_name) -> bool | None:
        form = self.forms.get(form_name)
        if not form:
            return None
        return form.get(field_name) == "1"

    def is_no(self, form_name, field_name) -> bool | None:
        form = self.forms.get(form_name)
        if not form:
            return None
        return form.get(field_name) == "0"

    @property
    def has_partner(self):
        return self.is_yes("about-you", "has_partner") and self.is_no(
            "about-you", "are_you_in_a_dispute"
        )

    @property
    def is_employed(self):
        return self.is_yes("about-you", "is_employed")

    @property
    def is_self_employed(self):
        return self.is_yes("about-you", "is_self_employed")

    @property
    def is_partner_employed(self):
        if not self.has_partner:
            return False
        return self.is_yes("about-you", "partner_is_employed")

    @property
    def is_partner_self_employed(self):
        if not self.has_partner:
            return False
        return self.is_yes("about-you", "partner_is_self_employed")


class Session(SecureCookieSession):
    SESSION_TIMEOUT = timedelta(minutes=30)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        eligibility = {}
        if args:
            eligibility = args[0].get("eligibility", {})
        self["eligibility"] = Eligibility(forms=eligibility.get("forms", {}))

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


class SessionInterface(SecureCookieSessionInterface):
    session_class = Session
