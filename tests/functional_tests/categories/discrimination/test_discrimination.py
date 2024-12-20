from playwright.sync_api import Page, expect
import pytest

where_form_routing = [
    pytest.param(
        ["Work - including colleagues,"],
        "Why were you discriminated against",
        id="single_answer",
    ),
    pytest.param(
        ["Work - including colleagues,", "School, college, university"],
        "Why were you discriminated against",
        id="multiple_answers",
    ),
    pytest.param(["not sure"], "Referral page", id="not_sure"),
    pytest.param(
        ["Health or care", "not sure"],
        "Why were you discriminated against",
        id="not_sure_and_answer",
    ),
]


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("selections,expected_heading", where_form_routing)
def test_discrimination_where(page: Page, selections: list, expected_heading: str):
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


why_form_routing = [
    pytest.param(
        ["Race, colour, ethnicity, nationality"],
        "Legal aid is available",
        id="single_answer",
    ),
    pytest.param(
        [
            "Disability, health condition, mental health condition",
            "Religion, belief, lack of religion",
        ],
        "Legal aid is available",
        id="multiple_answers",
    ),
    pytest.param(["None of these"], "Referral page", id="not_sure"),
    pytest.param(
        ["Religion, belief, lack of religion", "None of these"],
        "Legal aid is available",
        id="not_sure_and_answer",
    ),
]


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("selections,expected_heading", why_form_routing)
def test_discrimination_why(page: Page, selections: list, expected_heading: str):
    """
    Test the discrimination form with different combinations of selections.

    Args:
        page: Playwright page fixture
        selections: List of labels to check
        expected_heading: Text expected to be visible after submission
    """
    page.get_by_role("link", name="Discrimination").click()
    page.get_by_label("Work - including colleagues,").check()
    page.get_by_role("button", name="Continue").click()

    # Check all selected options
    for selection in selections:
        page.get_by_label(selection).check()

    # Submit form
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_text(expected_heading)).to_be_visible()
