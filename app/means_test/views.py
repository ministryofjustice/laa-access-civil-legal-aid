from flask.views import View, MethodView
from flask import render_template, url_for, redirect, session, request
from flask_babel import lazy_gettext as _
from werkzeug.datastructures import MultiDict

from app.means_test.api import update_means_test, get_means_test_payload
from app.means_test.forms.about_you import AboutYouForm
from app.means_test.forms.benefits import BenefitsForm, AdditionalBenefitsForm
from app.means_test.forms.property import MultiplePropertiesForm
from app.means_test.forms.income import IncomeForm
from app.means_test.forms.review import ReviewForm, BaseMeansTestForm


class FormsMixin:
    forms = {
        "about-you": AboutYouForm,
        "benefits": BenefitsForm,
        "property": MultiplePropertiesForm,
        "additional-benefits": AdditionalBenefitsForm,
        "income": IncomeForm,
    }


class MeansTest(FormsMixin, View):
    def __init__(self, current_form_class, current_name):
        self.form_class = current_form_class
        self.current_name = current_name

    def handle_multiple_properties_ajax_request(self, form):
        if "add-property" in request.form:
            form.properties.append_entry()
            form._submitted = False
            return render_template(self.form_class.template, form=form)

        # Handle removing a property
        elif "remove-property-2" in request.form or "remove-property-3" in request.form:
            form.properties.pop_entry()
            form._submitted = False
            return render_template(self.form_class.template, form=form)

        return None

    def dispatch_request(self):
        eligibility = session.get_eligibility()
        form_data = MultiDict(eligibility.forms.get(self.current_name, {}))
        form = self.form_class(request.form or form_data)
        if isinstance(form, MultiplePropertiesForm):
            response = self.handle_multiple_properties_ajax_request(form)
            if response is not None:
                return response

        # Todo: Handle invalidation of previous answers when current answer invalidates it
        #   i.e when user changes their answers and no longer in dispute or no longer on benefits
        if form.validate_on_submit():
            session.get_eligibility().add(self.current_name, form.data)
            next_page = url_for(f"means_test.{self.get_next_page(self.current_name)}")
            payload = get_means_test_payload(session.get_eligibility())
            update_means_test(payload)

            return redirect(next_page)
        return render_template(self.form_class.template, form=form)

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


class CheckYourAnswers(FormsMixin, MethodView):
    def get(self):
        eligibility = session.get_eligibility()
        means_test_summary = {}
        for key, form_class in self.forms.items():
            if key not in eligibility.forms:
                continue
            form_data = MultiDict(eligibility.forms.get(key, {}))
            form = form_class(form_data)
            means_test_summary[str(form.title)] = self.get_form_summary(form, key)
        params = {"means_test_summary": means_test_summary, "form": ReviewForm()}
        return render_template("means_test/review.html", **params)

    @staticmethod
    def get_form_summary(form: BaseMeansTestForm, form_name: str) -> list:
        summary = []
        for item in form.summary().values():
            answer_key = "text"
            if item["is_multiple"]:
                # Multiple items need to be separated by a new line
                answer_key = "markdown"

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
        return self.get()
