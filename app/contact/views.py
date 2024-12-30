from flask.views import View
from flask import render_template, redirect, url_for
from app.contact.forms import RFCContactForm


class RFCContactPage(View):
    template: str = None

    def __init__(self, template, *args, **kwargs):
        self.template = template

    def dispatch_request(self):
        form = RFCContactForm()

        if form.validate_on_submit():
            # Process the form data
            print("hello")

            # Redirect to a success or thank-you page
            return redirect(url_for("thank_you"))

        return render_template(self.template, form=form)
