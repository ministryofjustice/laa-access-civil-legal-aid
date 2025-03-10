import pytest
from flask import session
from app.main import inject_exit_this_page


class Category(dict):
    def __init__(self, exit_page, code="default_code"):
        super().__init__()
        self["exit_page"] = exit_page
        self["code"] = code


@pytest.mark.parametrize(
    "session_data, expected_output",
    [
        ({}, {"show_exit_this_page": False}),
        ({"category": None}, {"show_exit_this_page": False}),
        ({"category": Category(True, "domestic_abuse")}, {"show_exit_this_page": True}),
        ({"category": Category(False, "housing")}, {"show_exit_this_page": False}),
    ],
)
def test_inject_exit_this_page(session_data, expected_output, app):
    with app.test_request_context():
        session.clear()
        session.update(session_data)
        assert inject_exit_this_page() == expected_output
