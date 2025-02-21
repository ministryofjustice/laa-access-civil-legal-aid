from flask.views import View
from app.contact.forms import ContactUsForm, ReasonsForContactingForm
import logging
from flask import session, render_template, request, redirect, url_for
from app.api import cla_backend
from app.contact.notify.api import (
    NotifyEmailOrchestrator,
    create_and_send_confirmation_email,
)
from app.means_test.api import get_means_test_payload, update_means_test
from app.means_test.views import MeansTest

logger = logging.getLogger(__name__)


class ReasonForContacting(View):
    methods = ["GET", "POST"]
    template = "contact/rfc.html"

    def dispatch_request(self):
        form = ReasonsForContactingForm()
        if request.method == "GET":
            form.referrer.data = request.referrer or "Unknown"
        if form.validate_on_submit():
            result = cla_backend.post_reasons_for_contacting(form=form)
            next_step = form.next_step_mapping.get("*")
            logger.info("RFC Created Reference: %s", result.get("reference"))
            if result and "reference" in result:
                session[form.MODEL_REF_SESSION_KEY] = result["reference"]
            return redirect(url_for(next_step))
        return render_template(self.template, form=form)


class ContactUs(View):
    methods = ["GET", "POST"]
    template = "contact/contact.html"

    def __init__(self, template: str = None, attach_eligiblity_data: bool = False):
        if template:
            self.template = template
        self.attach_eligiblity_data = attach_eligiblity_data

    def dispatch_request(self):
        form = ContactUsForm()
        form_progress = MeansTest(ContactUsForm, "Contact us").get_form_progress(form)
        if form.validate_on_submit():
            payload = form.get_payload()
            # Catches duplicate case exceptions and redirect to error page
            cla_backend.post_case(
                payload=payload, attach_eligiblity_data=self.attach_eligiblity_data
            )
            # Add the extra notes to the eligibility object
            if self.attach_eligiblity_data:
                notes_data = form.data.get("extra_notes")
                session.get_eligibility().add_note("User problem", notes_data)
                eligibility_data = get_means_test_payload(session.get_eligibility())
                update_means_test(eligibility_data)
            # RFC Handling
            if ReasonsForContactingForm.MODEL_REF_SESSION_KEY in session:
                notes_data = form.data.get("extra_notes")
                cla_backend.update_reasons_for_contacting(
                    session[ReasonsForContactingForm.MODEL_REF_SESSION_KEY],
                    payload={
                        "case": session["case_reference"],
                        "other_reasons": notes_data,
                    },
                )
                del session[ReasonsForContactingForm.MODEL_REF_SESSION_KEY]
            # Email Handling
            callback_types = ["callback", "thirdparty"]
            session["callback_requested"] = (
                form.data.get("contact_type") in callback_types
            )
            session["contact_type"] = form.data.get("contact_type")
            requires_action_at, callback_time = ContactUsForm.get_callback_time(form)
            session["callback_time"] = callback_time
            email = form.get_email()
            if email:
                govuk_notify = NotifyEmailOrchestrator()
                data = form.data
                data["email"] = email
                create_and_send_confirmation_email(govuk_notify, data)
            return render_template(
                "contact/confirmation.html", data=session["case_reference"]
            )
        return render_template(self.template, form=form, form_progress=form_progress)
