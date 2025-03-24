from typing import List
from flask.views import View, MethodView
from flask import render_template, url_for, redirect, session, request
from flask_babel import lazy_gettext as _, gettext
from werkzeug.datastructures import MultiDict
from app.categories.constants import Category
from app.means_test.api import update_means_test, is_eligible
from app.means_test.constants import EligibilityState
from app.means_test.forms.about_you import AboutYouForm
from app.means_test.forms.benefits import BenefitsForm, AdditionalBenefitsForm
from app.means_test.forms.property import MultiplePropertiesForm
from app.means_test.forms.income import IncomeForm
from app.means_test.forms.savings import SavingsForm
from app.means_test.forms.outgoings import OutgoingsForm
from app.means_test.forms.review import ReviewForm, BaseMeansTestForm
from app.categories.models import CategoryAnswer, QuestionType
from app.means_test.payload import MeansTestPayload


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


class MeansTest(FormsMixin, View):
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

    def dispatch_request(self):
        eligibility = session.get_eligibility()
        form_data = eligibility.forms.get(self.current_name, {})
        form = self.form_class(formdata=request.form or None, data=form_data)
        if isinstance(form, MultiplePropertiesForm):
            response = self.handle_multiple_properties_ajax_request(form)
            if response is not None:
                return response

        if form.validate_on_submit():
            session.get_eligibility().add(self.current_name, form.data)
            next_page = url_for(f"means_test.{self.get_next_page(self.current_name)}")
            payload = MeansTestPayload()
            payload.update_from_session()

            response = update_means_test(payload)
            if "reference" not in response:
                raise ValueError("Eligibility reference not found in response")

            ec_reference = session.get("ec_reference")
            if request.method == "GET" and ec_reference:
                eligibility_result = is_eligible(ec_reference)
                # Once we are sure of the user's eligibility we should not ask the user subsequent questions
                # and instead ask them to confirm their answers before proceeding
                if eligibility_result in [EligibilityState.YES, EligibilityState.NO]:
                    return redirect(url_for("means_test.review"))

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
        def get_your_problem__no_description(category: Category) -> list[dict]:
            return [
                {
                    "key": {"text": _("The problem you need help with")},
                    "value": {"text": category.title},
                    "actions": {
                        "items": [
                            {"text": _("Change"), "href": url_for("categories.index")}
                        ],
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
                        "items": [
                            {"text": _("Change"), "href": url_for("categories.index")}
                        ],
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

        onward_questions = filter(
            lambda answer: answer.question_type == QuestionType.ONWARD, answers
        )

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
        ec_reference = session.get("ec_reference")
        eligibility = is_eligible(ec_reference)

        # Failsafe, if we are unsure of the eligibility state at this point send the user to the call centre
        if (
            eligibility == EligibilityState.YES
            or eligibility == EligibilityState.UNKNOWN
        ):
            return redirect(url_for("means_test.result.eligible"))

        if session.subcategory and session.subcategory.eligible_for_HLPAS:
            return redirect(url_for("means_test.result.hlpas"))
        return redirect(url_for("means_test.result.ineligible"))


class Ineligible(View):
    template = "means_test/refer.html"

    def __init__(self, template: str = None):
        if template:
            self.template = template

    def dispatch_request(self):
        category = session.category
        return render_template(self.template, category=category)


class Eligible(View):
    template = "categories/results/eligible.html"
