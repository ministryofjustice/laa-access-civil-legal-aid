from playwright.sync_api import Page, expect
import pytest

about_you_form_routing = [
    pytest.param(
        "No",
        [
            "Do you receive any benefits",
            "Do you have any children aged 15 or under?",
            "Do you have any dependants aged 16 or over?",
            "Do you own any property?",
            "Are you employed?",
            "Is your partner employed?",
            "Are you self-employed?",
            "Is your partner self-employed?",
            "Are you or your partner (if you have one) aged 60 or over?",
            "Do you have any savings or investments?",
            "Do you have any valuable items worth over £500 each?",
        ],
        id="all_no",
    ),
    pytest.param(
        "Yes",
        [
            "Do you receive any benefits",
            "Do you have any children aged 15 or under?",
            "Do you have any dependants aged 16 or over?",
            "Do you own any property?",
            "Are you employed?",
            "Is your partner employed?",
            "Are you self-employed?",
            "Is your partner self-employed?",
            "Are you or your partner (if you have one) aged 60 or over?",
            "Do you have any savings or investments?",
            "Do you have any valuable items worth over £500 each?",
        ],
        id="all_yes",
    ),
]


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("selection,expected_heading", about_you_form_routing)
def test_about_you(page: Page, selection: str, expected_heading: list):
    """
    Test the reason for contacting form with different combinations of selection.

    Args:
        page: Playwright page fixture
        selection: List of labels to check
        expected_heading: Text expected to be visible after submission
    """
    page.get_by_role("link", name="Housing, homelessness, losing your home").click()
    page.get_by_role("link", name="Homelessness").click()
    page.get_by_role("button", name="Check if you qualify financially").click()

    expect(page.get_by_text("About You")).to_be_visible()
    if selection == "No":
        page.locator("#has-partner-2").check()
    elif selection == "Yes":
        page.locator("#has-partner").check()
        expect(
            page.get_by_text("Are you in a dispute with your partner?")
        ).to_be_visible()
        expected_heading.insert(0, "Are you in a dispute with your partner?")

    for heading in expected_heading:
        form_group = page.get_by_role("group", name=heading)
        form_group.get_by_label(selection).check()

    if selection == "Yes":
        for each in page.locator("text=How many?").all():
            each.fill("1")

    # Submit form
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_text("Review your answers")).to_be_visible()
