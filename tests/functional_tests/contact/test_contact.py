from playwright.sync_api import Page, expect
import pytest

rfc_form_routing = [
    pytest.param(
        ["I don’t know how to answer a question"],
        "Why do you want to contact Civil Legal Advice?",
        id="single_answer",
    ),
    pytest.param(
        [
            "I don’t know how to answer a question",
            "My problem area isn’t covered",
            "Another reason",
        ],
        "Why do you want to contact Civil Legal Advice?",
        id="multiple_answers",
    ),
]


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("selections,expected_heading", rfc_form_routing)
def test_rfc_page(page: Page, selections: list, expected_heading: str):
    """
    Test the reason for contacting form with different combinations of selections.

    Args:
        page: Playwright page fixture
        selections: List of labels to check
        expected_heading: Text expected to be visible after submission
    """
    page.get_by_role("link", name="Contact us").click()

    # Check all selected options
    for selection in selections:
        page.get_by_label(selection).check()

    # Submit form
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_text(expected_heading)).to_be_visible()
