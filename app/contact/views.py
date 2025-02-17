from flask.views import View
from app.contact.forms import ContactUsForm, ReasonsForContactingForm
import logging
from flask import session, render_template
from app.api import cla_backend
from app.contact.notify.api import (
    NotifyEmailOrchestrator,
    create_and_send_confirmation_email,
)

logger = logging.getLogger(__name__)


class ContactUs(View):
    methods = ["GET", "POST"]
    template = "contact/contact.html"

    def __init__(self, template: str = None, attach_eligiblity_data: bool = False):
        if template:
            self.template = template
        self.attach_eligiblity_data = attach_eligiblity_data

    def dispatch_request(self):
        form = ContactUsForm()
        if form.validate_on_submit():
            # Add notes from tell us more about your problem
            # Welsh field change if welsh
            # Progress Bar
            # Domestic abuse exit this page
            payload = form.get_payload()
            # Catches duplicate case exceptions and redirect to error page
            try:
                result = cla_backend.post_case(
                    payload=payload, attach_eligiblity_data=self.attach_eligiblity_data
                )
            except Exception as e:
                if hasattr(e, "response") and e.response.status_code == 500:
                    return render_template("components/error_page.html")
            logger.info("API Response: %s", result)
            callback = ["callback", "thirdparty"]
            session["callback_requested"] = (
                True if form.data.get("contact_type") in callback else False
            )
            session["contact_type"] = form.data.get("contact_type")
            requires_action_at, formatted_time = ContactUsForm.get_callback_time(form)
            session["formatted_time"] = formatted_time
            email = form.get_email()
            if email:
                govuk_notify = NotifyEmailOrchestrator()
                data = form.data
                data["email"] = email
                create_and_send_confirmation_email(govuk_notify, data)
            if ReasonsForContactingForm.MODEL_REF_SESSION_KEY in session:
                cla_backend.update_reasons_for_contacting(
                    session[ReasonsForContactingForm.MODEL_REF_SESSION_KEY],
                    payload={"case": session["reference"]},
                )
                del session[ReasonsForContactingForm.MODEL_REF_SESSION_KEY]
            return render_template(
                "contact/confirmation.html", data=session["reference"]
            )
        return render_template(self.template, form=form)
