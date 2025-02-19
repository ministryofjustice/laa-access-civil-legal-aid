from flask.sessions import SecureCookieSession, SecureCookieSessionInterface
from app.categories.constants import Category
from flask import session
from dataclasses import dataclass
from datetime import timedelta
from app.categories.models import ScopeAnswer


@dataclass
class Eligibility:
    def __init__(self, forms, _notes):
        self.forms = forms
        self._notes = _notes

    forms: dict[str, dict]

    def add(self, form_name, data):
        self.forms[form_name] = data

    @property
    def category(self):
        return session.get("category", {}).get("chs_code")

    def is_yes(self, form_name, field_name) -> bool | None:
        form = self.forms.get(form_name)
        if not form:
            return False
        return form.get(field_name) == "1"

    def is_no(self, form_name, field_name) -> bool | None:
        form = self.forms.get(form_name)
        if not form:
            return False
        return form.get(field_name) == "0"

    @property
    def has_partner(self):
        return self.is_yes("about-you", "has_partner") and not self.is_yes(
            "about-you", "are_you_in_a_dispute"
        )

    @property
    def is_employed(self):
        return self.is_yes("about-you", "is_employed")

    @property
    def is_self_employed(self):
        return self.is_yes("about-you", "is_self_employed")

    @property
    def is_employed_or_self_employed(self):
        return self.is_yes("about-you", "is_employed") or self.is_yes(
            "about-you", "is_self_employed"
        )

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

    @property
    def has_savings(self):
        return self.is_yes("about-you", "have_savings")

    @property
    def has_valuables(self):
        return self.is_yes("about-you", "have_valuables")

    @property
    def has_children(self) -> bool:
        return self.is_yes("about-you", "have_children")

    @property
    def has_dependants(self) -> bool:
        return self.is_yes("about-you", "have_dependents")

    @property
    def on_benefits(self) -> bool:
        return self.is_yes("about-you", "on_benefits")

    @property
    def is_eligible_for_child_benefits(self) -> bool:
        return self.has_children or self.has_dependants

    @property
    def has_passported_benefits(self) -> bool:
        passported_benefits = [
            "pension_credit",
            "income_support",
            "job_seekers_allowance",
            "employment_support",
            "universal_credit",
        ]
        return self.on_benefits and any(
            benefit in passported_benefits
            for benefit in session.get_eligibility()
            .forms.get("benefits", {})
            .get("benefits", [])
        )

    @property
    def notes(self):
        return self._notes

    def add_note(self, key: str, note: str):
        self._notes[key] = note


class Session(SecureCookieSession):
    SESSION_TIMEOUT = timedelta(minutes=30)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        eligibility = {}
        if args:
            eligibility = args[0].get("eligibility", {})
        self["eligibility"] = Eligibility(forms=eligibility.get("forms", {}), _notes={})

    def update_eligibility(self, form_name, form_data):
        self["eligibility"].add(form_name, form_data)

    def get_eligibility(self):
        return self["eligibility"]

    def clear_eligibility(self):
        self["eligibility"] = Eligibility(forms={}, _notes={})

    @property
    def category(self) -> Category | None:
        """Get the category from the session.

        Returns:
            The category name if found, None otherwise
        """
        category_dict = self.get("category")
        if category_dict is None:
            return None
        if isinstance(category_dict, Category):
            return category_dict
        return Category.from_dict(category_dict)

    @category.setter
    def category(self, category: Category):
        current_category = self.category
        if current_category != category:
            self["category_answers"] = []
        self["category"] = category

    @property
    def has_children(self):
        # Todo: Needs implementation
        return True

    @property
    def has_dependants(self):
        # Todo: Needs implementation
        return True

    @property
    def category_answers(self) -> list[ScopeAnswer]:
        items: list[dict] = self.get("category_answers", [])
        category_answers = []
        for answer in items:
            if isinstance(answer["category"], dict):
                answer["category"] = Category.from_dict(answer["category"])
            category_answers.append(ScopeAnswer(**answer))

        return category_answers

    def set_category_question_answer(self, scope_answer: ScopeAnswer) -> None:
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

        answers: list[ScopeAnswer] = self.category_answers

        # Remove existing entry if present
        answers = [
            entry for entry in answers if entry.question != scope_answer.question
        ]

        answers.append(scope_answer)

        self["category_answers"] = answers

    def get_category_question_answer(self, question_title: str) -> str | None:
        """Retrieve an answer for a question from the session.

        Args:
            question_title: The title of the question to look up

        Returns:
            The stored answer string if found, None otherwise
        """
        answers = self.category_answers
        for answer in answers:
            if answer.question == question_title:
                return answer.answer_value

        return None


class SessionInterface(SecureCookieSessionInterface):
    session_class = Session
