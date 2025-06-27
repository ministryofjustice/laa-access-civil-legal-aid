from flask.views import View
from flask import session, url_for, redirect, render_template, request
from app.contact.forms.booking import BookingForm
from app.contact.forms.check_your_answers import CheckYourAnswers


class ContactView(View):
    forms = {
        "booking": BookingForm,
        "review": CheckYourAnswers,
    }

    def __init__(self, current_form_class, current_name):
        self.form_class = current_form_class
        self.current_name = current_name

    def dispatch_request(self):
        contact_forms = session["contact"].forms
        form_data = contact_forms.get(self.current_name, {})
        form = self.form_class(formdata=request.form or None, data=form_data)

        if form.validate_on_submit():
            session["contact"].add(self.current_name, form.data)
            next_page = url_for(f"contact_us.{self.get_next_page(self.current_name)}")

            return redirect(next_page)

        return self.render_form(form)

    def render_form(self, form):
        return render_template(
            self.form_class.template,
            form=form,
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
