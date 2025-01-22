from flask.views import View, MethodView
from flask import render_template, url_for, redirect, session

from app.means_test.api import update_means_test, get_payload as get_means_test_payload
from app.means_test.forms.about_you import AboutYouForm
from app.means_test.forms.benefits import BenefitsForm
from app.means_test.forms.property import PropertyForm
from app.means_test.forms.income import IncomeForm


class MeansTest(View):
    forms = {
        "about-you": AboutYouForm,
        "benefits": BenefitsForm,
        "property": PropertyForm,
        "income": IncomeForm,
    }

    def __init__(self, current_form_class, current_name):
        self.form_class = current_form_class
        self.current_name = current_name

    def dispatch_request(self):
        form = self.form_class()
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


class CheckYourAnswers(MethodView):
    def get(self):
        return render_template("means_test/review.html", data=session.get_eligibility())
