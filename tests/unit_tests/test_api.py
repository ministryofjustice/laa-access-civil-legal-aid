import pytest
from unittest.mock import Mock, patch
from flask_babel import LazyString
from app.api import BackendAPIClient
from datetime import datetime


class TestHostname:
    def test_hostname(self, api_client, app):
        with app.app_context():
            assert api_client.hostname == "http://backend-test.local"


class TestUrlConstruction:
    @pytest.mark.parametrize(
        "endpoint,expected",
        [
            ("/test", "http://backend-test.local/test"),
            ("test", "http://backend-test.local/test"),
            ("/test/", "http://backend-test.local/test/"),
        ],
    )
    def test_url_construction(self, api_client, endpoint, expected):
        assert api_client.url(endpoint) == expected


class TestCleanParams:
    def test_clean_params_with_lazy_string(self):
        params = {"key": LazyString(lambda: "value")}
        result = BackendAPIClient.clean_params(params)
        assert result == {"key": "value"}

    def test_clean_params_with_regular_dict(self):
        params = {"key": "value", "num": 123}
        result = BackendAPIClient.clean_params(params)
        assert result == params

    def test_clean_params_with_invalid_input(self):
        assert BackendAPIClient.clean_params("not-a-dict") is None


class TestGetRequest:
    @patch("requests.Session.send")
    def test_get_request(self, mock_send, api_client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.json.return_value = {"data": "test"}
        mock_send.return_value = mock_response

        result = api_client.get("/test", params={"key": "value"})

        assert result == {"data": "test"}
        assert mock_send.call_count == 1
        prepared_request = mock_send.call_args[0][0]
        assert prepared_request.method == "GET"
        assert "key=value" in prepared_request.url


class TestPostRequest:
    @patch("requests.Session.send")
    def test_post_request(self, mock_send, api_client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.json.return_value = {"status": "created"}
        mock_send.return_value = mock_response

        payload = {"test": "data"}
        result = api_client.post("/test", json=payload)

        assert result == {"status": "created"}
        assert mock_send.call_count == 1
        prepared_request = mock_send.call_args[0][0]
        assert prepared_request.method == "POST"


class TestHelpOrganisations:
    @patch("requests.Session.send")
    def test_get_help_organisations(self, mock_send, api_client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": ["org1", "org2"]}
        mock_send.return_value = mock_response

        result = api_client.get_help_organisations("test-category")

        assert result == ["org1", "org2"]
        prepared_request = mock_send.call_args[0][0]
        assert "article_category__name=test-category" in prepared_request.url


class TestReasonsForContacting:
    @patch("requests.Session.send")
    def test_post_reasons_for_contacting_with_form(self, mock_send, api_client):
        mock_form = Mock()
        mock_form.api_payload.return_value = {"form": "data"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_send.return_value = mock_response

        result = api_client.post_reasons_for_contacting(form=mock_form)

        assert result == {"status": "success"}
        prepared_request = mock_send.call_args[0][0]
        assert prepared_request.method == "POST"

    @patch("requests.Session.send")
    def test_post_reasons_for_contacting_with_payload(self, mock_send, api_client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_send.return_value = mock_response

        payload = {"custom": "payload"}
        result = api_client.post_reasons_for_contacting(payload=payload)

        assert result == {"status": "success"}
        prepared_request = mock_send.call_args[0][0]
        assert prepared_request.method == "POST"


# Test Callback
@pytest.fixture
def mock_slots():
    return [
        datetime(2025, 2, 21, 9, 0),
        datetime(2025, 2, 21, 9, 30),
        datetime(2025, 2, 22, 10, 0),
        datetime(2025, 2, 23, 10, 0),
    ]


@pytest.fixture
def next_7_days():
    return {
        datetime(2025, 2, 21).date(),
        datetime(2025, 2, 22).date(),
        datetime(2025, 2, 23).date(),
    }


class TestCallbackSlots:
    @pytest.fixture(autouse=True)
    def setup_method(self, mock_slots, next_7_days):
        self.client = BackendAPIClient()
        self.slots = mock_slots
        self.next_7_days = next_7_days

    def test_format_slots_by_day(self):
        result = self.client.format_slots_by_day(self.slots, self.next_7_days)

        expected = {
            "2025-02-21": [["0900", "9:00am to 9:30am"], ["0930", "9:30am to 10:00am"]],
            "2025-02-22": [["1000", "10:00am to 10:30am"]],
            "2025-02-23": [["1000", "10:00am to 10:30am"]],
        }

        assert result == expected
