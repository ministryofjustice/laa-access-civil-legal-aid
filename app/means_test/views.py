from flask.views import View, MethodView
from flask import render_template, url_for, redirect, session, request

from werkzeug.datastructures import MultiDict

from app.means_test.api import update_means_test, get_means_test_payload
from app.means_test.forms.about_you import AboutYouForm
from app.means_test.forms.benefits import BenefitsForm, AdditionalBenefitsForm
from app.means_test.forms.property import MultiplePropertiesForm
from app.means_test.forms.income import IncomeForm
from app.means_test.forms.savings import SavingsForm


class MeansTest(View):
    forms = {
        "about-you": AboutYouForm,
        "benefits": BenefitsForm,
        "additional-benefits": AdditionalBenefitsForm,
        "property": MultiplePropertiesForm,
        "savings": SavingsForm,
        "income": IncomeForm,
    }

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
        form = self.form_class(
            formdata=request.form or None, data=form_data if not request.form else None
        )
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

    def get_form_progress(self, current_form):
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

        is_about_you_completed = self.is_form_completed("about-you")
        return {
            "steps": forms,
            "current_step": current_form_key,
            "is_about_you_completed": is_about_you_completed,
        }


class CheckYourAnswers(MethodView):
    def get(self):
        return render_template("means_test/review.html", data=session.get_eligibility())
