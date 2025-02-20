from playwright.sync_api import Page, expect
import pytest
import re

rfc_form_routing = [
    pytest.param(
        ["I don’t know how to answer a question"],
        "Contact Civil Legal Advice",
        id="single_answer",
    ),
    pytest.param(
        [
            "I don’t know how to answer a question",
            "My problem area isn’t covered",
            "Another reason",
        ],
        "Contact Civil Legal Advice",
        id="multiple_answers",
    ),
    pytest.param(
        [],
        "Contact Civil Legal Advice",
        id="no_choice",
    ),
]


contact_form_routing = [
    pytest.param(
        {
            "Your full name": ["Test Name", "input"],
            "Select a contact option": ["I will call you", "radio"],
            "Email (optional)": ["test@email.com", "input"],
            "Street address (optional)": ["1 test street", "input"],
            "Tell us more about your problem (optional)": [
                "Test notes",
                "input",
            ],
            "Welsh": ["yes", "checkbox"],
        },
    ),
    pytest.param(
        {
            "Your full name": ["Test Name", "input"],
            "Select a contact option": ["Call me back", "radio"],
            "Phone number": ["123456789", "input"],
            "Select a time for us to call": ["Call on another day", "radio"],
            "Day": ["Select a time for us to call", "select"],
            "Can we say that we're calling from Civil Legal Advice?": ["Yes", "radio"],
            "Email (optional)": ["test@email.com", "input"],
            "Street address (optional)": ["1 test street", "input"],
            "Tell us more about your problem (optional)": [
                "Test notes",
                "input",
            ],
            "Text relay": ["Yes", "checkbox"],
        },
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


@pytest.mark.usefixtures("live_server")
def test_contact_page_rfc_routing(page: Page):
    """
    Test the contact page to ensure the correct url is shown for rfc.
    """
    page.get_by_role("link", name="Contact us").click()

    page.get_by_label("I’d prefer to speak to someone").check()

    page.get_by_role("button", name="Continue").click()

    expect(page).to_have_url(re.compile(".*/contact-us"))


@pytest.mark.usefixtures("live_server")
def test_contact_page_eligible_routing(page: Page):
    """
    Test the contact page to ensure the correct url is shown for eligible.
    """
    page.get_by_role("link", name="Discrimination").click()

    page.get_by_label("School, college, university or other education setting").check()
    page.get_by_role("button", name="Continue").click()

    page.get_by_label("Age").check()
    page.get_by_role("button", name="Continue").click()

    page.get_by_label("Yes").check()
    page.get_by_role("button", name="Continue").click()

    expect(page).to_have_url(re.compile(".*/eligible"))


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("contact_answers", contact_form_routing)
def test_contact_page_routing(page: Page, contact_answers: dict):
    """
    Test the contact page.
    """
    page.get_by_role("link", name="Contact us").click()

    page.get_by_label("I’d prefer to speak to someone").check()

    page.get_by_role("button", name="Continue").click()

    expect(
        page.get_by_role("heading", name="Contact Civil Legal Advice")
    ).to_be_visible()

    for question, answer in contact_answers.items():
        if answer[1] == "radio":
            page.get_by_label(answer[0]).first.check()
        elif answer[1] == "input":
            page.get_by_label(question).first.fill(answer[0])
        elif answer[1] == "select":
            page.get_by_role("group", name="Select a time for us to call").get_by_label(
                "Day", exact=True
            ).select_option(index=1)
            page.locator("#call_another_time").select_option(index=1)
        elif answer[1] == "checkbox":
            page.get_by_role("checkbox", name=question).first.check()

    page.get_by_role("button", name="Submit details").click()

    expect(page.get_by_role("heading", name="Confirmation Page")).to_be_visible()
