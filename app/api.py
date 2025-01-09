from urllib.parse import urljoin
import requests
from flask import current_app
from app.extensions import cache


class BackendAPIClient:
    checker_api_endpoint = ""

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

    def get(self, endpoint: str, **kwargs):
        """Make a GET request to the backend API.
        Args:
            endpoint (str): The endpoint to request
            kwargs: Any additional query parameters to pass to the backend
        Returns:
            dict: The JSON response from the backend
        """
        response = requests.get(url=self.url(endpoint), params=kwargs)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: dict):
        """Make a POST request to CLA Backend.
        Args:
            endpoint (str): The endpoint to request
            data (dict): The data to send to the backend
        Returns:
            dict: The JSON response from the backend
        """
        response = requests.post(url=self.url(endpoint), json=data)
        response.raise_for_status()
        return response.json()

    @cache.memoize(timeout=86400)  # 1 day
    def get_help_organisations(self, category: str):
        """Get help organisations for a given category, each unique set of arguments return value is cached for 24 hours.
        Args:
            category (str): An article category name
        Returns:
            List[str]: A list of help organisations
        """
        if not isinstance(category, str):
            return []
        params = {
            "article_category__name": category.title()  # CLA Backend requires the category name to be title case
        }
        response = self.get("checker/api/v1/organisation/", **params)
        return response["results"]


cla_backend = BackendAPIClient()
