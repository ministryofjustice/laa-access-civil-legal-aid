from flask.views import View
from app.contact.forms import (
    ContactUsForm,
    ReasonsForContactingForm,
    ConfirmationEmailForm,
)
import logging
from flask import (
    session,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    current_app,
)
from app.api import cla_backend
from app.contact.notify.api import notify
from app.means_test.api import is_eligible, EligibilityState
from app.means_test.views import MeansTest
from datetime import datetime
from app.categories.constants import (
    FinancialAssessmentReason,
    FinancialAssessmentStatus,
)
from app.categories.mixins import InScopeMixin


logger = logging.getLogger(__name__)


class ReasonForContacting(View):
    methods = ["GET", "POST"]
    template = "contact/rfc.html"

    def dispatch_request(self):
        form = ReasonsForContactingForm()
        if request.method == "GET":
            form.referrer.data = request.referrer or "Unknown"
        if form.validate_on_submit():
            # If the user has already raised a case we want to ensure their information is not included in multiple cases.
            if session.get("case_reference"):
                session.clear()
            result = cla_backend.post_reasons_for_contacting(form=form)
            next_step = form.next_step_mapping.get("*")
            logger.info("RFC Created Reference: %s", result.get("reference"))
            if result and "reference" in result:
                session[form.MODEL_REF_SESSION_KEY] = result["reference"]
            return redirect(url_for(next_step))
        return render_template(
            self.template,
            form=form,
            govukRebrand=current_app.config.get("GOVUK_REBRAND"),
        )


class ContactUs(View):
    methods = ["GET", "POST"]
    template = "contact/contact.html"

    def __init__(self, template: str = None, attach_eligibility_data: bool = False):
        if template:
            self.template = template
        self.attach_eligibility_data = attach_eligibility_data

    def dispatch_request(self):
        if session.get("case_reference", None):
            logger.error("FAILED contact page due to invalid session", exc_info=True)
            return redirect(url_for("main.session_expired"))
        form = ContactUsForm()
        form_progress = MeansTest(ContactUsForm, "Contact us").get_form_progress(form)
        if form.validate_on_submit():
            payload = form.get_payload()
            if not self.attach_eligibility_data:
                session.clear_eligibility()

            # If the user used the "Contact Us" journey rather than completing scope diagnosis then their
            # previous answers should not be attached to their case
            payload["scope_traversal"] = (
                session.get_scope_traversal()
                if ReasonsForContactingForm.MODEL_REF_SESSION_KEY not in session
                else {}
            )
            financial_status, financial_reason = self.get_financial_eligibility_status()
            payload["scope_traversal"]["financial_assessment_status"] = financial_status
            payload["scope_traversal"]["fast_track_reason"] = financial_reason

            session["case_reference"] = cla_backend.post_case(payload=payload)[
                "reference"
            ]
            logger.info(f"Case created {session['case_reference']}")

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
                    form.data.get("thirdparty_full_name"),
                    form.data.get("contact_number"),
                    form.data.get("thirdparty_contact_number"),
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
        return render_template(
            self.template,
            form=form,
            form_progress=form_progress,
            govukRebrand=current_app.config.get("GOVUK_REBRAND"),
        )

    @staticmethod
    def _attach_rfc_to_case(case_ref: str, rfc_ref: str):
        cla_backend.update_reasons_for_contacting(
            rfc_ref,
            payload={
                "case": case_ref,
            },
        )

    def get_financial_eligibility_status(self):
        return (
            FinancialAssessmentStatus.SKIPPED,
            FinancialAssessmentReason.MORE_INFO_REQUIRED,
        )


class FastTrackedContactUs(InScopeMixin, ContactUs):
    def get_financial_eligibility_status(self):
        reason_str = request.args.get("reason", "other")
        reason = FinancialAssessmentReason.get_reason_from_str(reason_str)
        return FinancialAssessmentStatus.FAST_TRACK, reason

    def dispatch_request(self):
        scope_check_redirect = self.ensure_in_scope()
        if scope_check_redirect:
            return scope_check_redirect

        return super().dispatch_request()


class EligibleContactUsPage(ContactUs):
    def get_financial_eligibility_status(self):
        eligibility_result = is_eligible(session.ec_reference)
        if eligibility_result.YES:
            return (
                FinancialAssessmentStatus.PASSED,
                FinancialAssessmentReason.MORE_INFO_REQUIRED,
            )
        elif eligibility_result.NO:
            return (
                FinancialAssessmentStatus.FAILED,
                FinancialAssessmentReason.MORE_INFO_REQUIRED,
            )

    def dispatch_request(self):
        if not session.ec_reference:
            return redirect(url_for("main.session_expired"))

        state = is_eligible(session.ec_reference)
        if state != EligibilityState.YES:
            return redirect(url_for("main.session_expired"))

        return super().dispatch_request()


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
            logger.error(
                "FAILED confirmation page due to invalid session", exc_info=True
            )
            return redirect(url_for("main.session_expired"))

        form = ConfirmationEmailForm()
        context = self.get_context()
        email_sent = False

        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        if form.validate_on_submit():
            # Send the email
            notify.create_and_send_confirmation_email(
                email_address=form.email.data,
                case_reference=context["case_reference"],
                callback_time=context["callback_time"],
                contact_type=context["contact_type"],
            )
            email_sent = True

        if request.method == "POST" and is_ajax:
            if email_sent:
                logger.info("Confirmation email sent")
                return jsonify(success=True, email=form.email.data)
            return jsonify(success=False, errors=form.errors), 400

        return render_template(
            self.template,
            form=form,
            confirmation_email=form.email.data if email_sent else None,
            email_sent=email_sent,
            **context,
            govukRebrand=current_app.config.get("GOVUK_REBRAND"),
        )
