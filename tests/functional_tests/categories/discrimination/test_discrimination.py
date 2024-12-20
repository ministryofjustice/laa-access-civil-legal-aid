from playwright.sync_api import Page, expect
import pytest

routing = [
    pytest.param(
        ["Work - including colleagues,"], "Why were you treated", id="single_answer"
    ),
    pytest.param(
        ["Work - including colleagues,", "School, college, university"],
        "Why were you treated",
        id="multiple_answers",
    ),
    pytest.param(["not sure"], "Referral page", id="not_sure"),
    pytest.param(
        ["Health or care", "not sure"], "Why were you treated", id="not_sure_and_answer"
    ),
]


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("selections,expected_heading", routing)
def test_discrimination_where_single_answer(
    page: Page, selections: list, expected_heading: str
):
    """
    Test the discrimination form with different combinations of selections.

    Args:
        page: Playwright page fixture
        selections: List of labels to check
        expected_heading: Text expected to be visible after submission
    """
    page.get_by_role("link", name="Discrimination").click()

    # Check all selected options
    for selection in selections:
        page.get_by_label(selection).check()

    # Submit form
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_text(expected_heading)).to_be_visible()
