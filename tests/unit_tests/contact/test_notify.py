import pytest
from unittest.mock import patch, MagicMock
from app.contact.notify.api import NotifyEmailOrchestrator, notify
from datetime import datetime


MOCK_GOVUK_NOTIFY_TEMPLATES = {
    "PUBLIC_CONFIRMATION_EMAIL_CALLBACK_REQUESTED_THIRDPARTY": {
        "en": "template-id-thirdparty-callback-en",
        "cy": "template-id-thirdparty-callback-cy",
    },
    "PUBLIC_CONFIRMATION_EMAIL_CALLBACK_REQUESTED": {
        "en": "template-id-callback-en",
        "cy": "template-id-callback-cy",
    },
    "PUBLIC_CONFIRMATION_NO_CALLBACK": {
        "en": "template-id-no-callback-en",
        "cy": "template-id-no-callback-cy",
    },
    "PUBLIC_CALLBACK_NOT_REQUESTED": {
        "en": "template-id-named-no-callback-en",
        "cy": "template-id-named-no-callback-cy",
    },
    "PUBLIC_CALLBACK_WITH_NUMBER": {
        "en": "template-id-personal-callback-en",
        "cy": "template-id-personal-callback-cy",
    },
    "PUBLIC_CALLBACK_THIRD_PARTY": {
        "en": "template-id-named-thirdparty-callback-en",
        "cy": "template-id-named-thirdparty-callback-cy",
    },
}


class TestNotifyEmailOrchestrator:
    def test_orchestrator_initialization(self, app):
        app.config["EMAIL_ORCHESTRATOR_URL"] = "https://email.orchestrator/"
        orchestrator = NotifyEmailOrchestrator()
        assert orchestrator.base_url == "https://email.orchestrator/"
        assert orchestrator.endpoint == "email"

    def test_orchestrator_url(self, app):
        app.config["EMAIL_ORCHESTRATOR_URL"] = "https://email.orchestrator/"
        orchestrator = NotifyEmailOrchestrator()
        assert orchestrator.url() == "https://email.orchestrator/email"

    @patch("requests.post")
    def test_send_email_success(self, mock_post, app):
        app.config["TESTING"] = False
        app.config["EMAIL_ORCHESTRATOR_URL"] = "https://fake-orchestrator.com"

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        orchestrator = NotifyEmailOrchestrator()
        result = orchestrator.send_email(
            "test@example.com", "template123", {"name": "Test"}
        )

        mock_post.assert_called_once()
        assert result is True

    @patch("requests.post")
    def test_send_email_failure(self, mock_post, app):
        app.config["TESTING"] = False
        app.config["EMAIL_ORCHESTRATOR_URL"] = "https://fake-orchestrator.com"

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = Exception("Error")
        mock_post.return_value = mock_response

        orchestrator = NotifyEmailOrchestrator()
        with pytest.raises(Exception):
            orchestrator.send_email("test@example.com", "template123", {"name": "Test"})

        mock_post.assert_called_once()


confirmation_email_test_scenarios = [
    # Scenario 1: No full name, callback requested, third party contact
    pytest.param(
        {
            "case_reference": "AB-1234-5678",
            "callback_time": datetime(2025, 1, 1, 12, 0),
            "contact_type": "thirdparty",
            "full_name": None,
            "third_party_name": None,
            "phone_number": None,
            "third_party_phone_number": None,
        },
        "template-id-thirdparty-callback-en",  # Expected template ID
        {
            "case_reference": "AB-1234-5678",
            "date_time": "formatted-time",  # Will be mocked
        },
        "en",  # Locale
        id="no_name_callback_thirdparty",
    ),
    # Scenario 2: No full name, callback requested, not third party
    pytest.param(
        {
            "case_reference": "CD-2345-6789",
            "callback_time": datetime(2025, 1, 1, 14, 0),
            "contact_type": "callback",
            "full_name": None,
            "third_party_name": None,
            "phone_number": None,
            "third_party_phone_number": None,
        },
        "template-id-callback-en",
        {
            "case_reference": "CD-2345-6789",
            "date_time": "formatted-time",
        },
        "en",
        id="no_name_callback_personal",
    ),
    # Scenario 3: No full name, no callback requested
    pytest.param(
        {
            "case_reference": "EF-3456-7890",
            "callback_time": None,
            "contact_type": None,
            "full_name": None,
            "third_party_name": None,
            "phone_number": None,
            "third_party_phone_number": None,
        },
        "template-id-no-callback-en",
        {
            "case_reference": "EF-3456-7890",
        },
        "en",
        id="no_name_no_callback",
    ),
    # Scenario 4: With full name, no callback requested
    pytest.param(
        {
            "case_reference": "GH-4567-8901",
            "callback_time": None,
            "contact_type": None,
            "full_name": "John Doe",
            "third_party_name": None,
            "phone_number": None,
            "third_party_phone_number": None,
        },
        "template-id-named-no-callback-en",
        {
            "full_name": "John Doe",
            "thirdparty_full_name": None,
            "case_reference": "GH-4567-8901",
            "date_time": "formatted-time",
        },
        "en",
        id="with_name_no_callback",
    ),
    # Scenario 5: With full name, callback requested, personal phone
    pytest.param(
        {
            "case_reference": "IJ-5678-9012",
            "callback_time": datetime(2025, 1, 2, 10, 0),
            "contact_type": "callback",
            "full_name": "Jane Smith",
            "third_party_name": None,
            "phone_number": "07700900000",
            "third_party_phone_number": None,
        },
        "template-id-personal-callback-en",
        {
            "full_name": "Jane Smith",
            "thirdparty_full_name": None,
            "case_reference": "IJ-5678-9012",
            "date_time": "formatted-time",
            "contact_number": "07700900000",
        },
        "en",
        id="with_name_callback_personal_phone",
    ),
    # Scenario 6: With full name, callback requested, third party phone
    pytest.param(
        {
            "case_reference": "KL-6789-0123",
            "callback_time": datetime(2025, 1, 3, 15, 0),
            "contact_type": "thirdparty",
            "full_name": "Alice Jones",
            "third_party_name": "Bob Brown",
            "phone_number": None,
            "third_party_phone_number": "07700900001",
        },
        "template-id-named-thirdparty-callback-en",
        {
            "full_name": "Alice Jones",
            "thirdparty_full_name": "Bob Brown",
            "case_reference": "KL-6789-0123",
            "date_time": "formatted-time",
            "contact_number": "07700900001",
        },
        "en",
        id="with_name_callback_thirdparty_phone",
    ),
    # Scenario 7: Welsh locale test
    pytest.param(
        {
            "case_reference": "MN-7890-1234",
            "callback_time": datetime(2025, 1, 4, 9, 0),
            "contact_type": "callback",
            "full_name": "Rhys Davies",
            "third_party_name": None,
            "phone_number": "07700900002",
            "third_party_phone_number": None,
        },
        "template-id-personal-callback-cy",
        {
            "full_name": "Rhys Davies",
            "thirdparty_full_name": None,
            "case_reference": "MN-7890-1234",
            "date_time": "formatted-time",
            "contact_number": "07700900002",
        },
        "cy",
        id="welsh_locale_test",
    ),
    # Scenario 8: Both phone numbers provided (personal number should be used)
    pytest.param(
        {
            "case_reference": "ST-0123-4567",
            "callback_time": datetime(2025, 1, 5, 11, 0),
            "contact_type": "callback",
            "full_name": "Test User",
            "third_party_name": "Helper Person",
            "phone_number": "07700900003",
            "third_party_phone_number": "07700900004",
        },
        "template-id-personal-callback-en",
        {
            "full_name": "Test User",
            "thirdparty_full_name": "Helper Person",
            "case_reference": "ST-0123-4567",
            "date_time": "formatted-time",
            "contact_number": "07700900003",  # Personal phone number should be used
        },
        "en",
        id="both_phone_numbers_provided",
    ),
]


@pytest.mark.parametrize(
    "input_data,expected_template_id,expected_personalisation,locale",
    confirmation_email_test_scenarios,
)
def test_generate_confirmation_email_data(
    input_data, expected_template_id, expected_personalisation, locale
):
    """
    Test the generate_confirmation_email_data function with various scenarios.

    Args:
        input_data: Dictionary containing all the input parameters for the function
        expected_template_id: The expected template ID that should be returned
        expected_personalisation: The expected personalisation dictionary that should be returned
        locale: The locale to mock (en or cy)
    """
    with (
        patch("app.contact.notify.api.get_locale") as mock_get_locale,
        patch(
            "app.contact.forms.ContactUsForm.format_callback_time",
            return_value="formatted-time",
        ),
        patch(
            "app.contact.notify.api.GOVUK_NOTIFY_TEMPLATES", MOCK_GOVUK_NOTIFY_TEMPLATES
        ),
    ):
        mock_get_locale.return_value = locale

        template_id, personalisation = notify.generate_confirmation_email_data(
            **input_data
        )

        assert template_id == expected_template_id
        assert personalisation == expected_personalisation
