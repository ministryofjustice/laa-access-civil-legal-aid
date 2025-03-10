import pytest
from unittest.mock import patch, ANY
from datetime import datetime, timezone
from app.contact.views import ConfirmationPage


class TestConfirmationPage:
    session_data = {
        "case_reference": "AB-1234-5678",
        "callback_time": datetime(2025, 3, 10, 10, 30, 0, tzinfo=timezone.utc),
        "contact_type": "callback",
        "category": {"code": "asylum_and_immigration"},
    }

    @pytest.fixture
    def mock_notify(self):
        with patch("app.contact.views.notify") as mock_notify:
            yield mock_notify

    def test_get_context(self, client):
        with client.session_transaction() as session:
            session.update(self.session_data)

        with client.application.test_request_context():
            with patch("app.contact.views.session", dict(session)):
                context = ConfirmationPage.get_context()

                assert context["case_reference"] == "AB-1234-5678"
                assert context["callback_time"] == datetime(
                    2025, 3, 10, 10, 30, 0, tzinfo=timezone.utc
                )
                assert context["contact_type"] == "callback"
                assert context["category"] == {"code": "asylum_and_immigration"}

    def test_get_confirmation_page(self, client):
        with client.session_transaction() as session:
            session.update(self.session_data)

        with patch("app.contact.views.render_template") as mock_render:
            mock_render.return_value = "Rendered Template"

            client.get("/confirmation")

            mock_render.assert_called_once_with(
                "contact/confirmation.html",
                form=ANY,
                case_reference="AB-1234-5678",
                callback_time=datetime(2025, 3, 10, 10, 30, 0, tzinfo=timezone.utc),
                contact_type="callback",
                category={"code": "asylum_and_immigration"},
                confirmation_email=None,
                email_sent=False,
            )

    def test_post_confirmation_page_valid_form(self, client, mock_notify):
        with client.session_transaction() as session:
            session.update(self.session_data)

        test_email = "test@example.com"

        with patch("app.contact.views.render_template") as mock_render:
            mock_render.return_value = "Rendered Template"

            client.post(
                "/confirmation", data={"email": test_email}, follow_redirects=True
            )

            mock_notify.create_and_send_confirmation_email.assert_called_once_with(
                email_address=test_email,
                case_reference="AB-1234-5678",
                callback_time=datetime(2025, 3, 10, 10, 30, 0, tzinfo=timezone.utc),
                contact_type="callback",
            )

            mock_render.assert_called_once_with(
                "contact/confirmation.html",
                form=ANY,
                case_reference="AB-1234-5678",
                callback_time=datetime(2025, 3, 10, 10, 30, 0, tzinfo=timezone.utc),
                contact_type="callback",
                category=ANY,
                confirmation_email=test_email,
                email_sent=True,
            )

    def test_post_confirmation_page_invalid_form(self, client, mock_notify):
        with client.session_transaction() as session:
            session.update(self.session_data)

        client.post(
            "/confirmation", data={"email": "invalid-email"}, follow_redirects=True
        )

        mock_notify.create_and_send_confirmation_email.assert_not_called()
