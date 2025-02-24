import logging

from app.contact.constants import GOVUK_NOTIFY_TEMPLATES
from flask import session, current_app
import requests
from app.main import get_locale


logger = logging.getLogger(__name__)


class NotifyEmailOrchestrator(object):
    def __init__(self):
        self.base_url = None
        if current_app.config["EMAIL_ORCHESTRATOR_URL"]:
            self.base_url = current_app.config["EMAIL_ORCHESTRATOR_URL"]
        elif not current_app.config["TESTING"]:
            raise EnvironmentError("EMAIL_ORCHESTRATOR_URL is not set.")
        self.endpoint = "email"

    def url(self):
        base_url = self.base_url if self.base_url.endswith("/") else self.base_url + "/"

        return base_url + self.endpoint

    def send_email(self, email_address, template_id, personalisation=None):
        """
        Sends an email to the Email Orchestration API.

            Parameters:
                email_address (str) - Email address of the receiver
                template_id (str) - The GOV.UK Notify template id
                personalisation (optional, dictionary) - The personalisation dictionary

            Returns:
                send_api_request (bool) - Will return True if the request was made successfully
                                          will return False if the EMAIL_ORCHESTRATOR_URL is not set or
                                          the application is in TESTING mode
        """
        if current_app.config["TESTING"]:
            logger.info("Application is in TESTING mode, will not send the request")
            return False

        if not self.base_url:
            logger.error("EMAIL_ORCHESTRATOR_URL is not set, unable to send email")
            return False

        data = {"email_address": email_address, "template_id": template_id}
        if personalisation:
            data["personalisation"] = personalisation

        response = requests.post(self.url(), json=data)

        if response.status_code != 201:
            response.raise_for_status()
        return True


def generate_confirmation_email_data(data):
    """
    Generates the data used in the sending of Gov Notify emails;
    includes paths for 5 different templates based on circumstance
    """
    data.update(
        {
            "case_ref": session.get("reference"),
            "callback_requested": session.get("callback_requested"),
            "contact_type": session.get("contact_type"),
        }
    )
    email_address = data["email"]
    template_id = ""

    # Path for confirmation email if no email is provided initially
    if "full_name" not in data:
        if session.get("callback_requested") is True:
            if session.get("contact_type") == "thirdparty":
                personalisation = {
                    "case_reference": data["case_ref"],
                    "date_time": session.get("callback_time"),
                }
                template_id = GOVUK_NOTIFY_TEMPLATES[
                    "PUBLIC_CONFIRMATION_EMAIL_CALLBACK_REQUESTED_THIRDPARTY"
                ][get_locale()[:2]]
            else:
                personalisation = {
                    "case_reference": data["case_ref"],
                    "date_time": session.get("callback_time"),
                }
                template_id = GOVUK_NOTIFY_TEMPLATES[
                    "PUBLIC_CONFIRMATION_EMAIL_CALLBACK_REQUESTED"
                ][get_locale()[:2]]
        else:
            personalisation = {"case_reference": data["case_ref"]}
            template_id = GOVUK_NOTIFY_TEMPLATES["PUBLIC_CONFIRMATION_NO_CALLBACK"][
                get_locale()[:2]
            ]

        return email_address, template_id, personalisation

    # Returns email if provided on contact form
    personalisation = {
        "full_name": data["full_name"],
        "thirdparty_full_name": data["thirdparty_full_name"],
        "case_reference": data["case_ref"],
        "date_time": session.get("callback_time"),
    }

    if session.get("callback_requested") is False:
        template_id = GOVUK_NOTIFY_TEMPLATES["PUBLIC_CALLBACK_NOT_REQUESTED"][
            get_locale()[:2]
        ]

        return email_address, template_id, personalisation

    # Decides between a personal callback or a third party callback
    if data["contact_number"]:
        template_id = GOVUK_NOTIFY_TEMPLATES["PUBLIC_CALLBACK_WITH_NUMBER"][
            get_locale()[:2]
        ]
        personalisation.update(contact_number=data["contact_number"])
    elif data["thirdparty_contact_number"]:
        template_id = GOVUK_NOTIFY_TEMPLATES["PUBLIC_CALLBACK_THIRD_PARTY"][
            get_locale()[:2]
        ]
        personalisation.update(contact_number=data["thirdparty_contact_number"])

    return email_address, template_id, personalisation


def create_and_send_confirmation_email(govuk_notify, data):
    email_address, template_id, personalisation = generate_confirmation_email_data(data)
    govuk_notify.send_email(
        email_address=email_address,
        template_id=template_id,
        personalisation=personalisation,
    )
