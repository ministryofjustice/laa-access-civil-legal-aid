import logging
from typing import List
from flask.views import View, MethodView
from flask import render_template, url_for, redirect, session, request
from flask_babel import lazy_gettext as _, gettext
from werkzeug.datastructures import MultiDict

from app.libs.eligibility_calculator.calculator import EligibilityChecker
from app.libs.eligibility_calculator.models import CaseData
from app.means_test.api import (
    is_eligible,
)
from app.categories.constants import Category
from app.means_test.constants import EligibilityState
from app.means_test.forms.about_you import AboutYouForm
from app.means_test.forms.benefits import BenefitsForm, AdditionalBenefitsForm
from app.means_test.forms.property import MultiplePropertiesForm
from app.means_test.forms.income import IncomeForm
from app.means_test.forms.savings import SavingsForm
from app.means_test.forms.outgoings import OutgoingsForm
from app.means_test.forms.review import ReviewForm, BaseMeansTestForm
from app.categories.models import CategoryAnswer, QuestionType
from app.categories.mixins import InScopeMixin
from app.means_test.payload import CFEMeansTestPayload

logger = logging.getLogger(__name__)


class FormsMixin:
    forms = {
        "about-you": AboutYouForm,
        "benefits": BenefitsForm,
        "additional-benefits": AdditionalBenefitsForm,
        "property": MultiplePropertiesForm,
        "savings": SavingsForm,
        "income": IncomeForm,
        "outgoings": OutgoingsForm,
    }

    def get_form_progress(self, current_form: BaseMeansTestForm) -> dict:
        """Gets the users progress through the means test. This is used to populate the progress bar."""
        from app.contact.forms import ContactUsForm

        forms = []
        current_form_key = ""

        is_means_test_complete = isinstance(current_form, (ReviewForm, ContactUsForm))

        for key, form in self.forms.items():
            form = form()
            if form.should_show():
                is_current = form.page_title == current_form.page_title
                if is_current:
                    current_form_key = key
                if not self.is_form_completed(key) and is_means_test_complete:
                    # Do not append incomplete means test forms if we are sure of the users eligibility
                    continue
                forms.append(
                    {
                        "key": key,
                        "title": form.page_title,
                        "url": url_for(f"means_test.{key}"),
                        "is_current": is_current,
                        "is_completed": self.is_form_completed(key)
                        and not current_form_key,  # Forms after the current form should not be marked as complete as prior answers can change subsequent questions
                    }
                )

        forms.append(
            {
                "key": "review",
                "title": ReviewForm.title,
                "url": url_for("means_test.review"),
                "is_current": current_form.page_title == ReviewForm.title,
                "is_completed": current_form.page_title == ContactUsForm.page_title,
            }
        )

        forms.append(
            {
                "key": "contact-us",
                "title": _("Contact information"),  # This is intentionally different from the page title
                "url": url_for("contact.contact_us"),
                "is_current": current_form.page_title == ContactUsForm.page_title,
                "is_completed": False,  # This can always be false as we don't show the progress bar after the contact us form
            }
        )

        num_completed_forms = (
            len([form for form in forms if form["is_completed"]])
        ) + 1  # Add 1 to account for the current form
        total_forms = len(forms)
        completion_percentage = num_completed_forms / total_forms * 100

        return {
            "steps": forms,
            "current_step": current_form_key,
            "completion_percentage": completion_percentage,
        }

    @staticmethod
    def is_form_completed(form_key: str):
        """Checks if the form has been completed by the user."""
        return form_key in session.get_eligibility().forms


class MeansTest(FormsMixin, InScopeMixin, View):
    def __init__(self, current_form_class, current_name):
        self.form_class = current_form_class
        self.current_name = current_name

    def handle_multiple_properties_ajax_request(self, form):
        if "add-property" in request.form:
            form.properties.append_entry()
        # Handle removing a property
        elif "remove-property-2" in request.form:
            form.properties.entries.pop(1)
        elif "remove-property-3" in request.form:
            form.properties.entries.pop(2)
        else:
            return None
        form._submitted = False
        return render_template(
            self.form_class.template,
            form=form,
            form_progress=self.get_form_progress(current_form=form),
        )

    def ensure_form_protection(self, current_form):
        if not current_form.should_show():
            logger.error(
                "FAILED ensuring form should show for %s",
                current_form.title,
                exc_info=True,
            )
            return redirect(url_for("main.session_expired"))

        progress = self.get_form_progress(current_form=current_form)

        # Ensure all forms leading upto the current form(current_form) are completed
        for form in progress["steps"]:
            if form["is_current"]:
                break
            if not form["is_completed"]:
                logger.error(
                    "FAILED ensuring form protection for %s",
                    current_form.title,
                    exc_info=True,
                )
                return redirect(url_for("main.session_expired"))
        return None

    def dispatch_request(self):
        in_scope_redirect = self.ensure_in_scope()
        if in_scope_redirect:
            return in_scope_redirect

        eligibility = session.get_eligibility()
        form_data = eligibility.forms.get(self.current_name, {})
        form = self.form_class(formdata=request.form or None, data=form_data)

        form_protection_redirect = self.ensure_form_protection(form)
        if form_protection_redirect:
            return form_protection_redirect

        if isinstance(form, MultiplePropertiesForm):
            response = self.handle_multiple_properties_ajax_request(form)
            if response is not None:
                return response

        if form.validate_on_submit():
            session.get_eligibility().add(self.current_name, form.data)
            next_page = url_for(f"means_test.{self.get_next_page(self.current_name)}")
            payload = CFEMeansTestPayload()
            payload.update_from_session()
            import json

            print(json.dumps(payload, indent=2))

            case_data = CaseData(**payload)
            ec = EligibilityChecker(case_data)
            eligibility_state, _, _, _ = ec.is_eligible_with_reasons()
            session["is_eligible"] = eligibility_state
            # Once we are sure of the user's eligibility we should not ask the user subsequent questions
            # and instead ask them to confirm their answers before proceeding.
            # We skip this check on the about-you page to match existing behaviour from CLA Public.
            if eligibility_state != EligibilityState.UNKNOWN and self.current_name not in ["about-you", "benefits"]:
                return redirect(url_for("means_test.review"))

            return redirect(next_page)

        return self.render_form(form)

    def render_form(self, form):
        return render_template(
            self.form_class.template,
            form=form,
            form_progress=self.get_form_progress(current_form=form),
        )

    def get_next_page(self, current_key):
        keys = list(self.forms.keys())  # Convert to list for easier indexing
        try:
            current_index = keys.index(current_key)
            # Look through remaining pages
            for next_key in keys[current_index + 1 :]:
                if self.forms[next_key].should_show():
                    return next_key
            return "review"  # No more valid pages found
        except ValueError:  # current_key not found
            return "review"


class CheckYourAnswers(FormsMixin, InScopeMixin, MethodView):
    template = "check-your-answers.html"

    def __init__(self, *args, **kwargs):
        self.form = ReviewForm()
        super().__init__(*args, **kwargs)

    def ensure_all_forms_are_complete(self):
        return None
        progress = self.get_form_progress(current_form=self.form)
        for form in progress["steps"]:
            print(progress["steps"])
            if not form["is_completed"]:
                logger.error(
                    "FAILED ensuring all forms are completed before the review page",
                    exc_info=True,
                )
                return redirect(url_for("main.session_expired"))

    def dispatch_request(self):
        # TODO: Store eligiblity in the session to prevent frequently requesting this.
        if is_eligible() in [
            EligibilityState.YES,
            EligibilityState.NO,
        ]:
            return super().dispatch_request()
        form_protection_redirect = self.ensure_all_forms_are_complete()
        if form_protection_redirect:
            return form_protection_redirect
        return super().dispatch_request()

    def get(self):
        eligibility = session.get_eligibility()
        means_test_summary = {}
        for key, form_class in self.forms.items():
            if key not in eligibility.forms:
                continue
            form_data = MultiDict(eligibility.forms.get(key, {}))
            form = form_class(form_data)
            if form.should_show():
                means_test_summary[str(form.page_title)] = self.get_form_summary(form, key)

        params = {
            "means_test_summary": means_test_summary,
            "form": self.form,
            "category": session.category,
            "category_answers": self.get_category_answers_summary(),
            "form_progress": self.get_form_progress(current_form=self.form),
        }
        return render_template("means_test/review.html", **params)

    @staticmethod
    def get_category_answers_summary():
        def get_your_problem__no_description(category: Category) -> list[dict]:
            return [
                {
                    "key": {"text": _("The problem you need help with")},
                    "value": {"text": category.title},
                    "actions": {
                        "items": [{"text": _("Change"), "href": url_for("categories.index")}],
                    },
                },
            ]

        def get_your_problem__with_description(category: Category) -> list[dict]:
            value = "\n".join(
                [
                    f"**{str(category.title)}**",
                    str(category.description),
                ]
            )
            return [
                {
                    "key": {"text": _("The problem you need help with")},
                    "value": {"markdown": value},
                    "actions": {
                        "items": [{"text": _("Change"), "href": url_for("categories.index")}],
                    },
                },
            ]

        answers: List[CategoryAnswer] = session.category_answers
        if not answers:
            return []

        category = session.category
        subcategory = session.subcategory if session.subcategory else category
        category_has_children = bool(getattr(category, "children"))
        if category_has_children:
            results = get_your_problem__with_description(subcategory)
        else:
            # if a category doesn't have children then it does not have subpages so we don't show the category description
            results = get_your_problem__no_description(subcategory)

        onward_questions = filter(lambda answer: answer.question_type == QuestionType.ONWARD, answers)

        for answer in onward_questions:
            answer_key = "text"
            answer_label = answer.answer_label
            if isinstance(answer_label, list):
                # Multiple items need to be separated by a new line
                answer_key = "markdown"
                answer_label = "\n".join([gettext(label) for label in answer_label])
            else:
                answer_label = gettext(answer_label)

            results.append(
                {
                    "key": {"text": gettext(answer.question)},
                    "value": {answer_key: answer_label},
                    "actions": {"items": [{"text": _("Change"), "href": answer.edit_url}]},
                }
            )
        return results

    @staticmethod
    def get_form_summary(form: BaseMeansTestForm, form_name: str) -> list:
        summary = []
        if isinstance(form.summary(), list):
            # Check if there's more than one property
            if len(form.summary()) > 1:
                for i, items in enumerate(form.summary(), start=1):
                    # Only add "Property {i}" heading if there are multiple properties
                    summary.append(
                        {
                            "key": {
                                "text": f"Property {i}",
                                "classes": "govuk-heading-m",
                            },
                            "value": {"text": ""},
                            "actions": {},
                        }
                    )

                    for key in items:
                        answer_key = "text"

                        if isinstance(items.get(key)["answer"], list):
                            answer_key = "markdown"
                            items.get(key)["answer"] = "\n".join(items.get(key)["answer"])

                        change_link = url_for(f"means_test.{form_name}", _anchor=items.get(key)["id"])
                        summary.append(
                            {
                                "key": {"text": items.get(key)["question"]},
                                "value": {answer_key: items.get(key)["answer"]},
                                "actions": {"items": [{"href": change_link, "text": _("Change")}]},
                            }
                        )
            else:
                # If there's only one property, don't add the heading, just display the questions and answers
                for items in form.summary():
                    for key in items:
                        answer_key = "text"

                        if isinstance(items.get(key)["answer"], list):
                            answer_key = "markdown"
                            items.get(key)["answer"] = "\n".join(items.get(key)["answer"])

                        change_link = url_for(f"means_test.{form_name}", _anchor=items.get(key)["id"])
                        summary.append(
                            {
                                "key": {"text": items.get(key)["question"]},
                                "value": {answer_key: items.get(key)["answer"]},
                                "actions": {"items": [{"href": change_link, "text": _("Change")}]},
                            }
                        )
            return summary

        for item in form.summary().values():
            answer_key = "text"
            if isinstance(item["answer"], list):
                # Multiple items need to be separated by a new line
                answer_key = "markdown"
                item["answer"] = "\n".join(item["answer"])

            change_link = url_for(f"means_test.{form_name}", _anchor=item["id"])
            summary.append(
                {
                    "key": {"text": item["question"]},
                    "value": {answer_key: item["answer"]},
                    "actions": {"items": [{"href": change_link, "text": _("Change")}]},
                }
            )
        return summary

    @staticmethod
    def post():
        eligibility = is_eligible()

        # Failsafe, if we are unsure of the eligibility state at this point send the user to the call centre
        if eligibility == EligibilityState.YES or eligibility == EligibilityState.UNKNOWN:
            logger.info(f"Eligibility check result successful - state is {eligibility}")
            return redirect(url_for("contact.eligible"))

        if session.subcategory and session.subcategory.eligible_for_HLPAS:
            logger.info(f"Eligibility check result HLPAS - state is {eligibility}")
            return redirect(url_for("means_test.result.hlpas"))

        logger.info(f"Eligibility check result unsuccessful - state is {eligibility}")
        return redirect(url_for("means_test.result.ineligible"))
