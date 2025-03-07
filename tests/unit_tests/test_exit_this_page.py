import pytest
from flask import session
from app.main import inject_exit_this_page


@pytest.mark.parametrize(
    "session_data, expected_output",
    [
        ({}, {"show_exit_this_page": False}),
        ({"category": {}}, {"show_exit_this_page": False}),
        ({"category": {"exit_page": True}}, {"show_exit_this_page": True}),
        ({"category": {"exit_page": False}}, {"show_exit_this_page": False}),
        (
            {"category": type("Category", (object,), {"exit_page": True})()},
            {"show_exit_this_page": True},
        ),
        (
            {"category": type("Category", (object,), {"exit_page": False})()},
            {"show_exit_this_page": False},
        ),
    ],
)
def test_inject_exit_this_page(session_data, expected_output, app):
    with app.test_request_context():
        session.update(session_data)
        assert inject_exit_this_page() == expected_output
