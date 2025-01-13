from flask import url_for
from playwright.sync_api import Page, expect
import pytest

rfc_form_routing = [
    pytest.param(
        ["Back to Work Bonus"],
        "Means test review",
        id="single_answer",
    ),
    pytest.param(
        [
            "Care in the community Direct Payment",
            "Carers’ Allowance",
            "Constant Attendance Allowance",
        ],
        "Means test review",
        id="multiple_answers",
    ),
    pytest.param(
        [],
        "Means test review",
        id="no_selection",
    ),
]


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("selections,expected_heading", rfc_form_routing)
def test_means_test_additional_benefits_page(
    page: Page, selections: list, expected_heading: str
):
    """
    Test the means test additional benefits page with different combinations of selections.

    Args:
        page: Playwright page fixture
        selections: List of labels to check
        expected_heading: Text expected to be visible after submission
    """
    page.goto(url=url_for("means_test.additional_benefits", _external=True))

    # Check all selected options
    for selection in selections:
        page.get_by_label(selection).check()

    # Submit form
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_text(expected_heading)).to_be_visible()
