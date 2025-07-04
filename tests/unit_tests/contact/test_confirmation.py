import pytest
from unittest.mock import patch, ANY
from datetime import datetime, timezone
from flask import url_for
from app.contact_backup.views import ConfirmationPage


@pytest.fixture
def valid_session(client):
    with client.session_transaction() as sess:
        sess["case_reference"] = "CASE123"
    return client


class TestConfirmationPage:
    session_data = {
        "case_reference": "AB-1234-5678",
        "callback_time": datetime(2025, 3, 10, 10, 30, 0, tzinfo=timezone.utc),
        "contact_type": "callback",
        "category": {"code": "asylum_and_immigration"},
    }

    @pytest.fixture
    def mock_notify(self):
        with patch("app.contact_backup.views.notify") as mock_notify:
            yield mock_notify

    def test_get_context(self, client):
        with client.session_transaction() as session:
            session.update(self.session_data)

        with client.application.test_request_context():
            with patch("app.contact_backup.views.session", dict(session)):
                context = ConfirmationPage.get_context()

                assert context["case_reference"] == "AB-1234-5678"
                assert context["callback_time"] == datetime(2025, 3, 10, 10, 30, 0, tzinfo=timezone.utc)
                assert context["contact_type"] == "callback"
                assert context["category"] == {"code": "asylum_and_immigration"}

    def test_get_confirmation_page(self, client):
        with client.session_transaction() as session:
            session.update(self.session_data)

        with patch("app.contact_backup.views.render_template") as mock_render:
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

        with patch("app.contact_backup.views.render_template") as mock_render:
            mock_render.return_value = "Rendered Template"

            client.post("/confirmation", data={"email": test_email}, follow_redirects=True)

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

        client.post("/confirmation", data={"email": "invalid-email"}, follow_redirects=True)

        mock_notify.create_and_send_confirmation_email.assert_not_called()

    def test_ajax_post_validation_failure(self, valid_session):
        with patch("app.contact_backup.views.ConfirmationEmailForm") as MockForm:
            mock_form = MockForm.return_value
            mock_form.validate_on_submit.return_value = False
            mock_form.errors = {"email": ["Invalid email address"]}

            response = valid_session.post(
                "/confirmation",
                data={"email": "invalid"},
                headers={"X-Requested-With": "XMLHttpRequest"},
            )

            assert response.status_code == 400
            json_data = response.get_json()
            assert json_data["success"] is False
            assert "email" in json_data["errors"]
            assert json_data["errors"]["email"] == ["Invalid email address"]


def test_confirmation_page_access_failure(app, client):
    response = client.get("/confirmation")
    assert response.status_code == 302
    assert response.location == url_for("main.session_expired")


def test_confirmation_page_access_success(app, client):
    with client.session_transaction() as session:
        session.update({"case_reference": "AB-1234-5678"})

    response = client.get("/confirmation")
    assert response.status_code == 200
