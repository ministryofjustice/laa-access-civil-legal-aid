import pytest
from flask import url_for
from playwright.sync_api import Page, expect


next_page_heading = "Check your answers and confirm"
rfc_form_routing = [
    pytest.param(
        ["Universal Credit"],
        next_page_heading,
        id="single_answer",
    ),
    pytest.param(
        [
            "Guarantee Credit",
            "Income Support",
            "Income-based Jobseeker's Allowance",
            "Income-related Employment and Support Allowance",
            "Universal Credit",
        ],
        next_page_heading,
        id="multiple_answers",
    ),
    pytest.param(
        ["Any other benefits"],
        "Your additional benefits",
        id="any_other_benefits",
    ),
    pytest.param(
        [],
        "Your money coming in",
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
def navigate_to_benefits(page: Page, answers: dict, navigate_to_means_test):
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
    expect(page.get_by_text("Which benefits do you receive?")).to_have_count(
        2
    )  # This checks for a count of two as the text also exists in the progress bar
    return page


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("answers", about_you_form_routing)
@pytest.mark.parametrize("selections,expected_heading", rfc_form_routing)
def test_means_test_benefits_page(page: Page, selections: list, expected_heading: str, navigate_to_benefits):
    """
    Test the means test benefits page with different combinations of selections.

    Args:
        page: Playwright page fixture
        selections: List of labels to check
        expected_heading: Text expected to be visible after submission
    """
    # Check all selected options
    for selection in selections:
        page.get_by_label(selection).check()

    # Submit form
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_role("heading", name=expected_heading)).to_be_visible()


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("answers", about_you_form_routing)
def test_additional_benefits_routing(page: Page, navigate_to_benefits):
    """
    Test the means test benefits page with different combinations of selections.

    Args:
        page: Playwright page fixture
        selections: List of labels to check
        expected_heading: Text expected to be visible after submission
    """
    page.get_by_role("checkbox", name="Any other benefits").click()

    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_role("heading", name="Your additional benefits")).to_be_visible()
    page.get_by_role("link", name="Completed page: About you").click()
    expect(page.get_by_role("heading", name="About you")).to_be_visible()
    page.get_by_role("group", name="Do you receive any benefits (including Child Benefit)?").get_by_label("No").click()
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_role("heading", name="Your money coming in")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_child_benefits_not_available(page: Page, client):
    page.goto(url=url_for("means_test.benefits", _external=True))
    expect(page.get_by_label("Child Benefit")).to_have_count(0)


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize(
    "about_you_answers",
    [
        {
            "Do you receive any benefits (including Child Benefit)?": "Yes",
            "Do you have any children aged 15 or under?": "Yes",
            "How many children aged 15 or under?": "1",
        }
    ],
)
def test_child_benefits_available_have_children(page: Page, complete_about_you_form):
    assert page.title() == "Which benefits do you receive? - GOV.UK"
    expect(page.get_by_label("Child Benefit")).to_have_count(1)


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize(
    "about_you_answers",
    [
        {
            "Do you receive any benefits (including Child Benefit)?": "Yes",
            "Do you have any dependants aged 16 or over?": "Yes",
            "How many dependants aged 16 or over?": "1",
        }
    ],
)
def test_child_benefits_available_have_dependents(page: Page, complete_about_you_form):
    assert page.title() == "Which benefits do you receive? - GOV.UK"
    expect(page.get_by_label("Child Benefit")).to_have_count(1)
