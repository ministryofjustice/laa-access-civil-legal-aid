import logging

from app.config import Config
import requests


log = logging.getLogger(__name__)


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
