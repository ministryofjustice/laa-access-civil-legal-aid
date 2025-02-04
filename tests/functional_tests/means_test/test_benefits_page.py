import pytest
from flask import url_for
from playwright.sync_api import Page, expect
from app.means_test import YES, NO


next_page_heading = "Review your answers"
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
def test_means_test_benefits_page(
    page: Page, selections: list, expected_heading: str, navigate_to_benefits
):
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
def test_child_benefits_not_available(page: Page, client):
    page.goto(url=url_for("means_test.benefits", _external=True))
    expect(page.get_by_label("Child Benefit")).to_have_count(0)


@pytest.mark.usefixtures("live_server")
def test_child_benefits_available_have_children(page: Page, client):
    #
    with client.session_transaction() as session:
        # update the session
        session.get_eligibility().add(
            "about-you", {"have_children": YES, "have_dependents": NO}
        )

    url = url_for("means_test.benefits", _external=True)
    response = client.get(url)
    assert response.status_code == 200  # Ensure the response is valid

    # Load the response HTML into the Playwright page
    page.set_content(response.data.decode("utf-8"))
    expect(page.get_by_label("Child Benefit")).to_have_count(1)


@pytest.mark.usefixtures("live_server")
def test_child_benefits_available_have_dependents(page: Page, client):
    #
    with client.session_transaction() as session:
        # update the session
        session.get_eligibility().add(
            "about-you", {"have_children": NO, "have_dependents": YES}
        )

    url = url_for("means_test.benefits", _external=True)
    response = client.get(url)
    assert response.status_code == 200  # Ensure the response is valid

    # Load the response HTML into the Playwright page
    page.set_content(response.data.decode("utf-8"))
    expect(page.get_by_label("Child Benefit")).to_have_count(1)
