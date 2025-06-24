from playwright.sync_api import Page, expect
import pytest

next_page_heading = "Your money coming in"
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

about_you_form_routing = [
    pytest.param(
        {
            "Do you have a partner": "No",
            "Do you receive any benefits": "Yes",
            "Do you have any children aged 15 or under?": "No",
            "Do you have any dependants aged 16 or over?": "No",
            "Do you own any property?": "No",
            "Are you employed?": "No",
            "Are you self-employed?": "No",
            "Are you or your partner (if you have one) aged 60 or over?": "No",
            "Do you have any savings or investments?": "No",
            "Do you have any valuable items worth over £500 each?": "No",
        },
    ),
]


@pytest.fixture
def navigate_to_additional_benefits(page: Page, answers: dict, navigate_to_means_test):
    expect(page.get_by_role("heading", name="About You")).to_be_visible()
    for question, answer in answers.items():
        form_group = page.get_by_role("group", name=question)
        if question == "Do you have a partner":
            locator = "#has_partner" if answer == "Yes" else "#has_partner-2"
            form_group.locator(locator).check()
            continue
        form_group.get_by_label(answer).first.check()
    # Submit form
    page.get_by_role("button", name="Continue").click()
    expect(page.locator('legend:text("Which benefits do you receive?")')).to_be_visible()
    page.get_by_label("Any other benefits").check()
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_role("heading", name="Your additional benefits")).to_be_visible()
    return page


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("answers", about_you_form_routing)
@pytest.mark.parametrize("selections,expected_heading", rfc_form_routing)
def test_means_test_additional_benefits_page(
    page: Page, selections: list, expected_heading: str, navigate_to_additional_benefits
):
    """
    Test the means test additional benefits page with different combinations of selections.

    Args:
        page: Playwright page fixture
        selections: List of labels to check
        expected_heading: Text expected to be visible after submission
    """
    # Check all selected options
    for selection in selections:
        page.get_by_label(selection).check()

    # Submit form
    page.get_by_role("button", name="Continue").scroll_into_view_if_needed()
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_text(expected_heading)).to_have_count(
        2
    )  # This checks for a count of two as the text also exists in the progress bar


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("answers", about_you_form_routing)
def test_additional_benefits_page_other_benefits_required(page, navigate_to_additional_benefits):
    """Test that Tell us whether you receive any other benefits question is required"""
    page.get_by_role("button", name="Continue").scroll_into_view_if_needed()
    page.get_by_role("button", name="Continue").click()

    # Select the anchor tag inside the error summary
    anchor = page.locator("div.govuk-error-summary a")
    assert anchor.inner_text() == "Tell us whether you receive any other benefits"


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("answers", about_you_form_routing)
def test_additional_benefits_page_total_other_benefits_required(page, navigate_to_additional_benefits):
    """Test that Tell us whether you receive any other benefits question is required when they select other benefits."""
    # Say yes to Do you receive any other benefits not listed above?
    page.get_by_label("Yes").check()
    page.get_by_role("button", name="Continue").scroll_into_view_if_needed()
    page.get_by_role("button", name="Continue").click()

    # Select the anchor tag inside the error summary
    anchor = page.locator("div.govuk-error-summary a")
    assert anchor.inner_text() == "Tell us how much you receive in other benefits"


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("answers", about_you_form_routing)
def test_additional_benefits_page_total_other_benefits(page, navigate_to_additional_benefits):
    # Say yes to Do you receive any other benefits not listed above?
    page.get_by_label("Yes").check()
    # Complete the If Yes, total amount of benefits not listed above question
    page.get_by_label("Amount").fill("100")
    page.get_by_label("Frequency").select_option(value="per_4week")

    page.get_by_role("button", name="Continue").scroll_into_view_if_needed()
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_role("heading", name=next_page_heading)).to_be_visible()
