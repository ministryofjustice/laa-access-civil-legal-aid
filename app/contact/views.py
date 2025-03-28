from flask.views import View
from app.contact.forms import (
    ContactUsForm,
    ReasonsForContactingForm,
    ConfirmationEmailForm,
)
import logging
from flask import session, render_template, request, redirect, url_for
from app.api import cla_backend
from app.contact.notify.api import notify
from app.means_test.api import update_means_test
from app.means_test.views import MeansTest
from datetime import datetime

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
            # Add the extra notes to the eligibility object
            if not self.attach_eligiblity_data:
                session.clear_eligibility()

            self._append_notes_to_eligibility_check(form.data.get("extra_notes"))

            session["case_reference"] = cla_backend.post_case(payload=payload)[
                "reference"
            ]

            if ReasonsForContactingForm.MODEL_REF_SESSION_KEY in session:
                self._attach_rfc_to_case(
                    session["case_reference"],
                    session[ReasonsForContactingForm.MODEL_REF_SESSION_KEY],
                )

            # Set callback time
            session["callback_time"]: datetime | None = form.get_callback_time()
            session["contact_type"] = form.data.get("contact_type")

            email_address = form.get_email()
            if email_address:
                notify.create_and_send_confirmation_email(
                    email_address,
                    session["case_reference"],
                    session["callback_time"],
                    session["contact_type"],
                    form.data.get("full_name"),
                    form.data.get("third_party_full_name"),
                    form.data.get("contact_number"),
                    form.data.get("third_party_contact_number"),
                )
            # Clears session data once form is submitted
            case_ref = session.get("case_reference")
            callback_time = session.get("callback_time")
            contact_type = session.get("contact_type")
            category = session.get("category")
            session.clear()
            session["case_reference"] = case_ref
            session["callback_time"] = callback_time
            session["contact_type"] = contact_type
            session["category"] = category
            return redirect(url_for("contact.confirmation"))
        return render_template(self.template, form=form, form_progress=form_progress)

    def _append_notes_to_eligibility_check(self, notes_data: str):
        if not notes_data or len(notes_data) == 0:
            return
        session.get_eligibility().add_note("User problem", notes_data)
        update_means_test(session.get_eligibility().formatted_notes)

    @staticmethod
    def _attach_rfc_to_case(case_ref: str, rfc_ref: str):
        cla_backend.update_reasons_for_contacting(
            rfc_ref,
            payload={
                "case": case_ref,
            },
        )


class ConfirmationPage(View):
    template = "contact/confirmation.html"
    methods = ["GET", "POST"]

    @classmethod
    def get_context(cls):
        return {
            "case_reference": session.get("case_reference"),
            "callback_time": session.get("callback_time"),
            "contact_type": session.get("contact_type"),
            "category": session.get("category", {}),
        }

    def dispatch_request(self):
        if not session.get("case_reference", None):
            logger.info("FAILED confirmation page due to invalid session")
            return redirect(url_for("main.session_expired"))
        form = ConfirmationEmailForm()
        context = self.get_context()
        email_sent = False

        if form.validate_on_submit():
            notify.create_and_send_confirmation_email(
                email_address=form.email.data,
                case_reference=context["case_reference"],
                callback_time=context["callback_time"],
                contact_type=context["contact_type"],
            )
            email_sent = True

        return render_template(
            self.template,
            form=form,
            confirmation_email=form.email.data if email_sent else None,
            email_sent=email_sent,
            **context,
        )
