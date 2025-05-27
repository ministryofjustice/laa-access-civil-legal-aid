import logging
from flask import current_app
import requests
from datetime import datetime

from app import get_locale
from app.contact.notify.templates import GOVUK_NOTIFY_TEMPLATES
from app.contact.helpers import format_callback_time

logger = logging.getLogger(__name__)


class NotifyEmailOrchestrator(object):
    @property
    def base_url(self):
        return current_app.config["EMAIL_ORCHESTRATOR_URL"]

    def __init__(self):
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

    def create_and_send_confirmation_email(
        self,
        email_address: str,
        case_reference: str,
        callback_time: datetime | None = None,
        contact_type: str | None = None,
        full_name: str | None = None,
        third_party_name: str | None = None,
        phone_number: str | None = None,
        third_party_phone_number: str | None = None,
    ):
        template_id, personalisation = self.generate_confirmation_email_data(
            case_reference,
            callback_time,
            contact_type,
            full_name,
            third_party_name,
            phone_number,
            third_party_phone_number,
        )
        notify.send_email(
            email_address=email_address,
            template_id=template_id,
            personalisation=personalisation,
        )

    @staticmethod
    def generate_confirmation_email_data(
        case_reference: str,
        callback_time: datetime | None = None,
        contact_type: str | None = None,
        full_name: str | None = None,
        third_party_name: str | None = None,
        phone_number: str | None = None,
        third_party_phone_number: str | None = None,
    ) -> (str, str):
        """Generates the data used in the sending of the confirmation Gov Notify emails."""
        formatted_callback_time = format_callback_time(callback_time)
        callback_requested = callback_time is not None

        template_id = ""
        locale = "cy" if get_locale().startswith("cy") else "en"

        if not full_name:
            if callback_requested:
                if contact_type == "thirdparty":
                    personalisation = {
                        "case_reference": case_reference,
                        "date_time": formatted_callback_time,
                    }
                    template_id = GOVUK_NOTIFY_TEMPLATES[
                        "PUBLIC_CONFIRMATION_EMAIL_CALLBACK_REQUESTED_THIRDPARTY"
                    ][locale]
                else:
                    personalisation = {
                        "case_reference": case_reference,
                        "date_time": formatted_callback_time,
                    }
                    template_id = GOVUK_NOTIFY_TEMPLATES[
                        "PUBLIC_CONFIRMATION_EMAIL_CALLBACK_REQUESTED"
                    ][locale]
            else:
                personalisation = {"case_reference": case_reference}
                template_id = GOVUK_NOTIFY_TEMPLATES["PUBLIC_CONFIRMATION_NO_CALLBACK"][
                    locale
                ]

            return template_id, personalisation

        personalisation = {
            "full_name": full_name,
            "thirdparty_full_name": third_party_name,
            "case_reference": case_reference,
            "date_time": formatted_callback_time,
        }

        if callback_requested is False:
            template_id = GOVUK_NOTIFY_TEMPLATES["PUBLIC_CALLBACK_NOT_REQUESTED"][
                locale
            ]
            return template_id, personalisation

        # Decides between a personal callback or a third party callback
        if phone_number:
            template_id = GOVUK_NOTIFY_TEMPLATES["PUBLIC_CALLBACK_WITH_NUMBER"][locale]
            personalisation.update(contact_number=phone_number)
        elif third_party_phone_number:
            template_id = GOVUK_NOTIFY_TEMPLATES["PUBLIC_CALLBACK_THIRD_PARTY"][locale]
            personalisation.update(contact_number=third_party_phone_number)

        return template_id, personalisation


notify = NotifyEmailOrchestrator()
