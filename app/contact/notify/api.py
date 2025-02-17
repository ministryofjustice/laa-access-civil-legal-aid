import logging

from app.config import Config
from app.contact.constants import GOVUK_NOTIFY_TEMPLATES
from flask import session, request
import requests


log = logging.getLogger(__name__)


def get_locale():
    if request and request.cookies.get("locale"):
        return request.cookies.get("locale")[:2]
    language_keys = [key for key, _ in Config.get("LANGUAGES", {})]
    return request.accept_languages.best_match(language_keys) or "en"


class NotifyEmailOrchestrator(object):
    def __init__(self):
        self.base_url = None
        if Config.EMAIL_ORCHESTRATOR_URL:
            self.base_url = Config.EMAIL_ORCHESTRATOR_URL
        elif not Config.TESTING:
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
        if Config.TESTING:
            log.info("Application is in TESTING mode, will not send the request")
            return False

        if not self.base_url:
            log.error("EMAIL_ORCHESTRATOR_URL is not set, unable to send email")
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
    try:
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
                        "date_time": session.get("formatted_time"),
                    }
                    template_id = GOVUK_NOTIFY_TEMPLATES[
                        "PUBLIC_CONFIRMATION_EMAIL_CALLBACK_REQUESTED_THIRDPARTY"
                    ][get_locale()[:2]]
                else:
                    personalisation = {
                        "case_reference": data["case_ref"],
                        "date_time": session.get("formatted_time"),
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
            "date_time": session.get("formatted_time"),
        }

        if session.get("callback_requested") is False:
            template_id = GOVUK_NOTIFY_TEMPLATES["PUBLIC_CALLBACK_NOT_REQUESTED"][
                get_locale()[:2]
            ]

            return email_address, template_id, personalisation

        # Decides between a personal callback or a third party callback
        if data["callback"]["contact_number"]:
            template_id = GOVUK_NOTIFY_TEMPLATES["PUBLIC_CALLBACK_WITH_NUMBER"][
                get_locale()[:2]
            ]
            personalisation.update(contact_number=data["callback"]["contact_number"])
        elif data["thirdparty"]["contact_number"]:
            template_id = GOVUK_NOTIFY_TEMPLATES["PUBLIC_CALLBACK_THIRD_PARTY"][
                get_locale()[:2]
            ]
            personalisation.update(contact_number=data["thirdparty"]["contact_number"])

        return email_address, template_id, personalisation
    except Exception as error:
        log.warning("Error Reference: {}".format(str(error)))
        raise error


def create_and_send_confirmation_email(govuk_notify, data):
    try:
        email_address, template_id, personalisation = generate_confirmation_email_data(
            data
        )
        govuk_notify.send_email(
            email_address=email_address,
            template_id=template_id,
            personalisation=personalisation,
        )
    except Exception as error:
        log.warning("Error Reference: {}".format(str(error)))
        raise error
