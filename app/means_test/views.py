from typing import List
from flask.views import View, MethodView
from flask import render_template, url_for, redirect, session, request
from flask_babel import lazy_gettext as _, gettext
from werkzeug.datastructures import MultiDict
from app.means_test.api import (
    update_means_test,
    get_means_test_payload,
    is_eligible,
    EligibilityState,
)
from app.means_test.forms.about_you import AboutYouForm
from app.means_test.forms.benefits import BenefitsForm, AdditionalBenefitsForm
from app.means_test.forms.property import MultiplePropertiesForm
from app.means_test.forms.income import IncomeForm
from app.means_test.forms.savings import SavingsForm
from app.means_test.forms.outgoings import OutgoingsForm
from app.means_test.forms.review import ReviewForm, BaseMeansTestForm
from app.categories.models import CategoryAnswer
from app.categories.mixins import InScopeMixin


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


class MeansTest(FormsMixin, InScopeMixin, View):
    def __init__(self, current_form_class, current_name):
        self.form_class = current_form_class
        self.current_name = current_name

    def handle_multiple_properties_ajax_request(self, form):
        if "add-property" in request.form:
            form.properties.append_entry()
            form._submitted = False
            return render_template(
                self.form_class.template,
                form=form,
                form_progress=self.get_form_progress(current_form=form),
            )

        # Handle removing a property
        elif "remove-property-2" in request.form or "remove-property-3" in request.form:
            form.properties.pop_entry()
            form._submitted = False
            return render_template(self.form_class.template, form=form)

        return None

    def ensure_form_protection(self, current_form):
        progress = self.get_form_progress(current_form=current_form)
        # Ensure all forms leading upto the current form(current_form) are completed
        for form in progress["steps"]:
            if form["is_current"]:
                break
            if not form["is_completed"]:
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
            payload = get_means_test_payload(session.get_eligibility())
            update_means_test(payload)

            return redirect(next_page)
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

    @staticmethod
    def is_form_completed(form_key: str):
        """Checks if the form has been completed by the user."""
        return form_key in session.get_eligibility().forms

    def get_form_progress(self, current_form: BaseMeansTestForm) -> dict:
        """Gets the users progress through the means test. This is used to populate the progress bar."""

        forms = []
        current_form_key = ""

        for key, form in self.forms.items():
            form = form()
            if form.should_show():
                is_current = form.page_title == current_form.page_title
                if is_current:
                    current_form_key = key
                forms.append(
                    {
                        "key": key,
                        "title": form.page_title,
                        "url": url_for(f"means_test.{key}"),
                        "is_current": is_current,
                        "is_completed": self.is_form_completed(key),
                    }
                )

        num_completed_forms = (
            len([form for form in forms if form["is_completed"]]) + 1
        )  # Add 1 to account for the current form
        total_forms = len(forms) + 2  # Add 2 to count for the review & contact pages
        completion_percentage = num_completed_forms / total_forms * 100

        return {
            "steps": forms,
            "current_step": current_form_key,
            "completion_percentage": completion_percentage,
        }


class CheckYourAnswers(FormsMixin, MethodView):
    template = "check-your-answers.html"

    def get(self):
        eligibility = session.get_eligibility()
        means_test_summary = {}
        for key, form_class in self.forms.items():
            if key not in eligibility.forms:
                continue
            form_data = MultiDict(eligibility.forms.get(key, {}))
            form = form_class(form_data)
            if form.should_show():
                means_test_summary[str(form.page_title)] = self.get_form_summary(
                    form, key
                )

        params = {
            "means_test_summary": means_test_summary,
            "form": ReviewForm(),
            "category": session.category,
            "category_answers": self.get_category_answers_summary(),
        }
        return render_template("means_test/review.html", **params)

    @staticmethod
    def get_category_answers_summary():
        def get_your_problem__no_description():
            return [
                {
                    "key": {"text": _("The problem you need help with")},
                    "value": {"text": session.category.title},
                    "actions": {
                        "items": [
                            {"text": _("Change"), "href": url_for("categories.index")}
                        ],
                    },
                },
            ]

        def get_your_problem__with_description(first_answer):
            value = "\n".join(
                [
                    f"**{str(first_answer.category.title)}**",
                    str(first_answer.category.description),
                ]
            )
            return [
                {
                    "key": {"text": _("The problem you need help with")},
                    "value": {"markdown": value},
                    "actions": {
                        "items": [{"text": _("Change"), "href": first_answer.edit_url}],
                    },
                },
            ]

        answers: List[CategoryAnswer] = session.category_answers
        if not answers:
            return []

        category = session.category
        category_has_children = bool(getattr(category, "children"))
        if category_has_children:
            if answers[0].question_type_is_sub_category:
                results = get_your_problem__with_description(answers.pop(0))
            else:
                # Sometimes there is only one answer and it was an onward question.
                # However we still need to show 2 items: 'The problem you need help with' and the onward question
                # Example journey:
                #   -> Children, families, relationships
                #   -> If there is domestic abuse in your family
                #   -> Are you worried about someone's safety?
                #
                # Then the two items need be shown in `About the problem` section:
                #   The `The problem you need help with` should be Domestic abuse with its description
                #   And the `Are you worried about someone's safety` onward question
                first_answer = CategoryAnswer(**answers[0].__dict__)
                first_answer.question_page = "categories.index"
                results = get_your_problem__with_description(first_answer)
        else:
            # if a category doesn't have children then it does not have subpages so we don't show the category description
            results = get_your_problem__no_description()

        for answer in answers:
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
                    "actions": {
                        "items": [{"text": _("Change"), "href": answer.edit_url}]
                    },
                }
            )
        return results

    @staticmethod
    def get_form_summary(form: BaseMeansTestForm, form_name: str) -> list:
        summary = []
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

    def post(self):
        if is_eligible(session.ec_reference) == EligibilityState.YES:
            return redirect(url_for("app.eligible"))
        return redirect(url_for("categories.results.refer"))
