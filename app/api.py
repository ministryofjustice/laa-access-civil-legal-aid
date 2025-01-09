from urllib.parse import urljoin
import requests
from flask_babel import LazyString
from flask import current_app
import logging
from app.extensions import cache

logger = logging.getLogger(__name__)


class BackendAPIClient:
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
        cleaned_params = self.clean_params(
            params
        )  # Clean the params, covering LazyStrings to strings

        request = requests.Request(
            method=method.upper(),
            url=self.url(endpoint),
            params=cleaned_params,
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
        return self.post("checker/api/v1/reasons-for-contacting/", json=payload)


cla_backend = BackendAPIClient()
