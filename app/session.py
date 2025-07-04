from flask.sessions import SecureCookieSession, SecureCookieSessionInterface
from app.categories.constants import (
    Category,
    get_category_from_code,
    get_subcategory_from_code,
)
from flask import session
from dataclasses import dataclass
from datetime import timedelta
from app.categories.models import CategoryAnswer, QuestionType
from flask_babel import LazyString
from app.api import cla_backend


@dataclass
class Contact:
    forms: dict[str, dict]

    def add(self, form_name, data):
        self.forms[form_name] = data

    @property
    def time_slots(self) -> list:
        if "_time_slots" not in session:
            session["_time_slots"] = cla_backend.get_time_slots(num_days=8)
        return session["_time_slots"]

    @property
    def third_party_time_slots(self) -> list:
        if "_third_party_time_slots" not in session:
            session["_third_party_time_slots"] = cla_backend.get_time_slots(num_days=8, is_third_party_callback=True)
        return session["_third_party_time_slots"]


@dataclass
class Eligibility:
    def __init__(self, forms, _notes=None):
        self.forms = forms
        self._notes = _notes or {}

    forms: dict[str, dict]

    def add(self, form_name, data):
        self.forms[form_name] = data

    @property
    def has_partner(self):
        return self.forms.get("about-you", {}).get("has_partner", False) and not self.forms.get("about-you", {}).get(
            "in_dispute", False
        )

    @property
    def owns_property(self) -> bool:
        return self.forms.get("about-you", {}).get("own_property", False)

    @property
    def is_employed(self):
        return self.forms.get("about-you", {}).get("is_employed", False)

    @property
    def is_self_employed(self):
        return self.forms.get("about-you", {}).get("is_self_employed", False)

    @property
    def is_employed_or_self_employed(self):
        return self.forms.get("about-you", {}).get("is_employed") or self.forms.get("about-you", {}).get(
            "is_self_employed", False
        )

    @property
    def is_partner_employed(self):
        if not self.has_partner:
            return False
        return self.forms.get("about-you", {}).get("partner_is_employed")

    @property
    def is_partner_self_employed(self):
        if not self.has_partner:
            return False
        return self.forms.get("about-you", {}).get("partner_is_self_employed")

    @property
    def has_savings(self):
        return self.forms.get("about-you", {}).get("has_savings", False)

    @property
    def has_valuables(self):
        return self.forms.get("about-you", {}).get("has_valuables", False)

    @property
    def has_children(self) -> bool:
        return self.forms.get("about-you", {}).get("has_children", False)

    @property
    def has_dependants(self) -> bool:
        return self.forms.get("about-you", {}).get("has_dependants", False)

    @property
    def on_benefits(self) -> bool:
        return self.forms.get("about-you", {}).get("on_benefits", False)

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
            for benefit in session.get_eligibility().forms.get("benefits", {}).get("benefits", [])
        )

    @property
    def notes(self):
        return self._notes

    @property
    def formatted_notes(self):
        def format_note(note_item):
            return "{key}:\n{note}".format(key=note_item[0], note=note_item[1])

        return {"notes": "\n\n".join(map(format_note, self.notes.items()))}

    def add_note(self, key: str, note: str):
        self._notes[key] = note


class Session(SecureCookieSession):
    SESSION_TIMEOUT = timedelta(minutes=30)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        eligibility = {}
        contact = {}
        if args:
            eligibility = args[0].get("eligibility", {})
            contact = args[0].get("contact", {})
        self["eligibility"] = Eligibility(forms=eligibility.get("forms", {}), _notes={})
        self["contact"] = Contact(forms=contact.get("forms", {}))

    def clear_category(self):
        if self.category:
            self.pop("category")
        if self.get("category_answers"):
            self["category_answers"] = []

    def update_eligibility(self, form_name, form_data):
        self["eligibility"].add(form_name, form_data)

    def get_eligibility(self):
        return self["eligibility"]

    def clear_eligibility(self):
        self["eligibility"] = Eligibility(forms={}, _notes={})

    @property
    def ec_reference(self):
        return self.get("_ec_reference", None)

    @ec_reference.setter
    def ec_reference(self, ec_reference):
        self["_ec_reference"] = ec_reference

    @property
    def category(self) -> Category | None:
        """Get the category from the session.

        Returns:
            The category name if found, None otherwise
        """
        category_dict = self.get("category")
        if category_dict is None:
            return None

        return self._category_from_dict_from_session_storage(category_dict)

    @category.setter
    def category(self, category: Category):
        current_category = self.category
        if current_category and current_category.code != category.code:
            self["category_answers"] = []
        self["category"] = self._category_to_dict_for_session_storage(category)

    @staticmethod
    def _category_to_dict_for_session_storage(category: Category):
        data = {"code": category.code}
        if category.parent_code:
            data["parent_code"] = category.parent_code
        return data

    @staticmethod
    def _category_from_dict_from_session_storage(category_dict: dict):
        parent_code = category_dict.get("parent_code", None)
        if parent_code:
            category = get_category_from_code(parent_code)
            return category.children[category_dict["code"]]
        else:
            return get_category_from_code(category_dict["code"])

    @property
    def subcategory(self):
        """Returns the subcategory based on category answers.

        Returns:
            Category: The subcategory object if found, None otherwise.

        Raises:
            ValueError: If multiple SUB_CATEGORY questions are found.
        """
        result = None

        for answer in self.category_answers:
            if answer.question_type == QuestionType.SUB_CATEGORY:
                if result is not None:
                    raise ValueError("User has multiple subcategory answers")

                result = get_subcategory_from_code(answer.category.parent_code, answer.category.code)

        return result

    @property
    def has_children(self):
        # Todo: Needs implementation
        return True

    @property
    def has_dependants(self):
        # Todo: Needs implementation
        return True

    @property
    def in_scope(self):
        category = self.subcategory or self.category
        return bool(category and category.in_scope)

    @property
    def category_answers(self) -> list[CategoryAnswer]:
        items: list[dict] = self.get("category_answers", [])
        category_answers = []
        for item in items:
            answer = item.copy()
            answer["category"] = self._category_from_dict_from_session_storage(answer["category"])
            category_answers.append(CategoryAnswer(**answer))

        return category_answers

    @staticmethod
    def _untranslate_category_answer(category_answer: CategoryAnswer):
        """Remove translation from the category_answer object"""
        category_answer_dict = {}
        for key, value in category_answer.__dict__.items():
            if isinstance(value, list):
                values = []
                for item in value:
                    if isinstance(item, LazyString):
                        values.append(item._args[0])
                    else:
                        values.append(item)
                value = values
            elif isinstance(value, LazyString):
                value = value._args[0]
            category_answer_dict[key] = value

        return CategoryAnswer(**category_answer_dict)

    def set_category_question_answer(self, category_answer: CategoryAnswer) -> None:
        """Store a question-answer pair with the question category in the session.

        Args:
            question_title: The question text
            answer: The answer text
            category: The category name

        Side effects:
            Updates session['category_answers'] list
        """

        # If the user changes subcategory we should reset their onward question answers.
        if category_answer.question_type == QuestionType.SUB_CATEGORY and self.subcategory:
            is_changing_sub_cat = category_answer.answer_value != self.subcategory.code
            if is_changing_sub_cat:
                self["category_answers"] = [
                    ans
                    for ans in self["category_answers"]
                    if ans.get("question_type") not in [QuestionType.ONWARD, QuestionType.SUB_CATEGORY]
                ]

        # Remove translation from the category_answer object before saving
        category_answer = self._untranslate_category_answer(category_answer)

        if "category_answers" not in self:
            self["category_answers"] = []
        if category_answer.category.parent_code:
            session.category = get_category_from_code(category_answer.category.parent_code)
        else:
            session.category = category_answer.category

        answers: list[CategoryAnswer] = self.category_answers

        # Update existing entry if present
        question_exists = False
        for i in range(len(answers)):
            if answers[i].question == category_answer.question:
                answers[i] = category_answer
                question_exists = True
        if not question_exists:
            answers.append(category_answer)

        category_answers = []
        for answer in answers:
            answer_dict = answer.__dict__
            answer_dict["category"] = self._category_to_dict_for_session_storage(answer.category)
            category_answers.append(answer_dict)

        self["category_answers"] = category_answers

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

    def remove_category_question_answer(self, question_title: str) -> None:
        """Remove a question-answer pair from the session.

        Args:
            question_title: The title of the question to remove

        """
        if "category_answers" not in self:
            return

        answers: list[dict[str, str]] = self["category_answers"]

        # Remove existing entry if present
        answers = [entry for entry in answers if entry["question"] != question_title]

        self["category_answers"] = answers

    def get_scope_traversal(self):
        """Used to populate the users' case data with their answers from this service."""

        def get_users_answers(answers: list[CategoryAnswer]) -> list[dict]:
            """Only get the fields that we need to store in the backend."""
            return [
                {
                    "question": answer.question,
                    "answer": answer.answer_label,
                    "type": answer.question_type,
                }
                for answer in answers
            ]

        category_information = (
            {"name": self.category.title._args[0], "code": self.category.chs_code} if self.category else None
        )

        subcategory_information = (
            {
                "name": self.subcategory.title._args[0],  # Get the non-translated string
                "description": self.subcategory.description._args[0],
            }
            if self.subcategory
            else None
        )

        return {
            "scope_answers": get_users_answers(self.category_answers),
            "category": category_information,
            "subcategory": subcategory_information,
        }

    def at_risk_of_harm(self):
        answer = self.get_category_question_answer("Are you worried about someone's safety?")
        if answer == "yes":
            return True
        return False


class SessionInterface(SecureCookieSessionInterface):
    session_class = Session
