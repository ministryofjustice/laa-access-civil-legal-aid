from flask import url_for
from playwright.sync_api import Page, expect
import pytest

next_page_heading = "Review your answers"
rfc_form_routing = [
    pytest.param(
        ["Back to Work Bonus", "No"],
        next_page_heading,
        id="single_answer",
    ),
    pytest.param(
        [
            "Care in the community Direct Payment",
            "Carers’ Allowance",
            "Constant Attendance Allowance",
            "No",
        ],
        next_page_heading,
        id="multiple_answers",
    ),
    pytest.param(
        [],
        "Your additional benefits",
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
    page.goto(url=url_for("means_test.additional-benefits", _external=True))

    # Check all selected options
    for selection in selections:
        page.get_by_label(selection).check()

    # Submit form
    page.get_by_role("button", name="Continue").scroll_into_view_if_needed()
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_text(expected_heading)).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_additional_benefits_page_other_benefits_required(page):
    """Test that Tell us whether you receive any other benefits question is required"""
    page.goto(url=url_for("means_test.additional-benefits", _external=True))
    page.get_by_role("button", name="Continue").scroll_into_view_if_needed()
    page.get_by_role("button", name="Continue").click()

    # Select the anchor tag inside the error summary
    anchor = page.locator("div.govuk-error-summary a")
    assert anchor.inner_text() == "Tell us whether you receive any other benefits"


@pytest.mark.usefixtures("live_server")
def test_additional_benefits_page_total_other_benefits_required(page):
    """Test that Tell us whether you receive any other benefits question is required when they select other benefits."""
    page.goto(url=url_for("means_test.additional-benefits", _external=True))
    # Say yes to Do you receive any other benefits not listed above?
    page.get_by_label("Yes").check()
    page.get_by_role("button", name="Continue").scroll_into_view_if_needed()
    page.get_by_role("button", name="Continue").click()

    # Select the anchor tag inside the error summary
    anchor = page.locator("div.govuk-error-summary a")
    assert anchor.inner_text() == "Tell us how much you receive in other benefits"


@pytest.mark.usefixtures("live_server")
def test_additional_benefits_page_total_other_benefits(page):
    page.goto(url=url_for("means_test.additional-benefits", _external=True))
    # Say yes to Do you receive any other benefits not listed above?
    page.get_by_label("Yes").check()
    # Complete the If Yes, total amount of benefits not listed above question
    page.get_by_label("Amount").fill("100")
    page.get_by_label("Frequency").select_option(value="per_4week")

    page.get_by_role("button", name="Continue").scroll_into_view_if_needed()
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_text(next_page_heading)).to_be_visible()
