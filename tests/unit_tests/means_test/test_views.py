import pytest
from unittest import mock
from flask import url_for
from app.session import Session
from app.means_test.views import MeansTest, FormsMixin
from app.session import Eligibility


@pytest.fixture
def mock_benefits_should_show():
    """Mock the session's get_eligibility method properly."""
    with mock.patch("app.means_test.forms.benefits.session") as benefits_session:
        benefits_session.get_eligibility = mock.Mock(
            return_value=Eligibility(forms={"about-you": {"on_benefits": True}})
        )
        yield benefits_session


def test_form_protection_in_scope(app, client):
    with app.app_context():
        with mock.patch.object(
            Session, "in_scope", new_callable=mock.PropertyMock
        ) as mock_in_scope:
            mock_in_scope.return_value = True
            view = MeansTest(FormsMixin.forms["about-you"], "about-you")
            with mock.patch.object(
                view,
                "render_form",
            ) as mock_render_form:
                view.dispatch_request()
                assert mock_render_form.called is True


def test_form_protection_not_in_scope(app, client):
    with app.app_context():
        with mock.patch.object(
            Session, "in_scope", new_callable=mock.PropertyMock
        ) as mock_in_scope:
            mock_in_scope.return_value = False
            view = MeansTest(FormsMixin.forms["about-you"], "about-you")
            response = view.dispatch_request()
            assert response.status_code == 302
            assert response.location == url_for("main.session_expired")


def test_form_protection_sequence_failed(app, client):
    """User needs to complete about-you before going to benefits"""
    with app.app_context():
        with mock.patch.object(
            Session, "in_scope", new_callable=mock.PropertyMock
        ) as mock_in_scope:
            mock_in_scope.return_value = True
            view = MeansTest(FormsMixin.forms["benefits"], "benefits")
            ensure_form_protection = view.ensure_form_protection
            with mock.patch.object(
                view,
                "ensure_form_protection",
            ) as mock_ensure_form_protection:
                # Allow the mock to call the original method while still tracking calls.
                mock_ensure_form_protection.side_effect = ensure_form_protection
                response = view.dispatch_request()
                assert mock_ensure_form_protection.called is True
                assert response.status_code == 302
                assert response.location == url_for("main.session_expired")


def test_form_protection_sequence_success(app, client, mock_benefits_should_show):
    """User needs to complete about-you before going to benefits"""
    with app.app_context():
        with mock.patch.object(
            Session, "in_scope", new_callable=mock.PropertyMock
        ) as mock_in_scope:
            mock_in_scope.return_value = True
            view = MeansTest(FormsMixin.forms["benefits"], "benefits")
            ensure_form_protection = view.ensure_form_protection
            with mock.patch.object(
                view,
                "ensure_form_protection",
            ) as mock_ensure_form_protection:
                # Allow the mock to call the original method while still tracking calls.
                mock_ensure_form_protection.side_effect = ensure_form_protection
                with mock.patch.object(
                    view,
                    "get_form_progress",
                ) as mock_get_form_progress:
                    mock_get_form_progress.return_value = {
                        "steps": [
                            {
                                "key": "about-you",
                                "title": "About you",
                                "is_current": False,
                                "is_completed": True,
                            },
                            {
                                "key": "benefits",
                                "title": "Benefits",
                                "is_current": True,
                                "is_completed": False,
                            },
                        ]
                    }
                    with mock.patch.object(
                        view,
                        "render_form",
                    ) as mock_render_form:
                        view.dispatch_request()
                        assert mock_ensure_form_protection.called is True
                        assert mock_render_form.called is True
