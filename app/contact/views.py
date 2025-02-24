from flask import render_template
from flask.views import View


class ConfirmationPage(View):
    template = "contact/confirmation.html"

    @staticmethod
    def get_context():
        return {}

    def dispatch_request(self):
        return render_template(self.template, **self.get_context())
