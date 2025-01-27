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
        next_page_heading,
        id="no_selection",
    ),
]


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("selections,expected_heading", rfc_form_routing)
def test_means_test_benefits_page(page: Page, selections: list, expected_heading: str):
    """
    Test the means test benefits page with different combinations of selections.

    Args:
        page: Playwright page fixture
        selections: List of labels to check
        expected_heading: Text expected to be visible after submission
    """

    url = url_for("means_test.benefits", _external=True)
    page.goto(url=url)
    # Check all selected options
    for selection in selections:
        page.get_by_label(selection).check()

    # Submit form
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_text(expected_heading)).to_be_visible()


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
