from urllib.parse import urljoin
import requests
from flask_babel import LazyString
from flask import current_app, session
import logging
from datetime import datetime
from app.extensions import cache

logger = logging.getLogger(__name__)


class BackendAPIClient:
    CALLBACK_API_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

    @property
    def hostname(self):
        return current_app.config["CLA_BACKEND_URL"]

    def url(self, endpoint: str):
        """Build the full URL for an endpoint.

        Args:
            endpoint: The API endpoint path

        Returns:
            The complete URL
        """
        # Use urljoin to properly handle path joining
        return urljoin(self.hostname.rstrip("/") + "/", endpoint.lstrip("/"))

    @staticmethod
    def clean_params(params):
        if not isinstance(params, dict):
            return None

        clean_params = {}
        for key, value in params.items():
            if isinstance(value, LazyString):
                clean_params[key] = str(value)
            else:
                clean_params[key] = value
        return clean_params

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        json: dict | None = None,
    ) -> dict:
        """Makes an HTTP request with logging to cla_backend.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            params: Optional query parameters to append to the URL
            json: Optional JSON data to send in the request body

        Returns:
            The parsed JSON response from the server
        """
        if not endpoint.endswith("/"):  # CLA Backend requires trailing slashes
            endpoint = f"{endpoint}/"

        if params:
            params = self.clean_params(
                params
            )  # Clean the params, covering LazyStrings to strings

        request = requests.Request(
            method=method.upper(),
            url=self.url(endpoint),
            params=params,
            json=json,
        ).prepare()

        logging.info(f"Request {request.method}: {request.url}")

        # Send the request and capture response
        response = requests.Session().send(request)

        logging.info(
            f"Response from {request.url}: {response.status_code} {response.reason}"
        )

        response.raise_for_status()
        return response.json()

    def get(self, endpoint: str, params: dict = None):
        """Make a GET request to the backend API.
        Args:
            endpoint (str): The endpoint to request
            params: Any additional query parameters to pass to the backend
        Returns:
            dict: The JSON response from the backend
        """
        return self._make_request(method="GET", endpoint=endpoint, params=params)

    def post(self, endpoint: str, json: dict):
        """Make a POST request to CLA Backend.
        Args:
            endpoint (str): The endpoint to request
            json (dict): The data to send to the backend
        Returns:
            dict: The JSON response from the backend
        """
        return self._make_request(method="POST", endpoint=endpoint, json=json)

    def patch(self, endpoint: str, json: dict):
        """Make a PATCH request to CLA Backend.
        Args:
            endpoint (str): The endpoint to request
            json (dict): The data to send to the backend
        Returns:
            dict: The JSON response from the backend
        """
        return self._make_request(method="PATCH", endpoint=endpoint, json=json)

    @cache.memoize(timeout=86400)  # 1 day
    def get_help_organisations(self, category: str):
        """Get help organisations for a given category, each unique set of arguments return value is cached for 24 hours.
        Args:
            category (str): An article category name
        Returns:
            List[str]: A list of help organisations
        """
        params = {"article_category__name": category}
        response = self.get("checker/api/v1/organisation/", params=params)
        return response["results"]

    def post_reasons_for_contacting(self, form=None, payload=None):
        if payload is None:
            payload = {}
        payload = form.api_payload() if form else payload
        return self.post("checker/api/v1/reasons_for_contacting/", json=payload)

    def get_time_slots(self, num_days=8, is_third_party_callback=False):
        params = {"third_party_callback": is_third_party_callback, "num_days": num_days}
        slots = self.get(
            "checker/api/v1/callback_time_slots/",
            params=params,
        )["slots"]
        slots = [
            datetime.strptime(slot, self.CALLBACK_API_DATETIME_FORMAT) for slot in slots
        ]

        return slots

    def post_case(self, payload=None):
        contact_endpoint = "checker/api/v1/case"
        payload["eligibility_check"] = session.get("ec_reference")

        response = self.post(contact_endpoint, json=payload)
        return response

    def update_reasons_for_contacting(self, reference, payload=None):
        return self.patch(
            f"checker/api/v1/reasons_for_contacting/{reference}", json=payload
        )


cla_backend = BackendAPIClient()
