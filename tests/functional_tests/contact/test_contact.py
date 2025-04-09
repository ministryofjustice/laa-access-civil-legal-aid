from playwright.sync_api import Page, expect
import pytest
import re
from flask import url_for


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


''' Test to be updated once review your answers is in
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
        "Your money coming in",
        id="all_no_route",
    ),]

@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("answers,route_to", about_you_form_routing)
def test_contact_page_eligible_routing(page: Page, answers: dict, route_to: str):
    """
    Test the contact page to ensure the correct url is shown for eligible.
    """
    page.get_by_role("link", name="Discrimination").click()

    page.get_by_label("School, college, university or other education setting").check()
    page.get_by_role("button", name="Continue").click()

    page.get_by_label("Age").check()
    page.get_by_role("button", name="Continue").click()

    page.get_by_label("No").check()
    page.get_by_role("button", name="Continue").click()

    page.get_by_role("button", name="Check if you qualify financially").click()

    expect(page.get_by_role("heading", name="About You")).to_be_visible()
    for question, answer in answers.items():
        form_group = page.get_by_role("group", name=question)
        if question == "Do you have a partner":
            locator = "#has_partner" if answer == "Yes" else "#has_partner-2"
            form_group.locator(locator).check()
            continue
        form_group.get_by_label(answer).first.check()

    page.get_by_label("Income Support").check()
    page.get_by_role("button", name="Continue").click()

    # Submit form
    page.get_by_role("button", name="Continue").click()

    expect(page).to_have_url(re.compile(".*/eligible"))
'''

fast_track_routing = [
    pytest.param(
        [
            "Domestic abuse",
            "Help to keep yourself safe and protect children",
            {"type": "form", "selector": "Yes"},
            {"endpoint": "contact.contact_us_fast_tracked", "reason": "harm"},
        ]
    ),
    pytest.param(
        [
            "Domestic abuse",
            "Forced Marriage",
            {"type": "form", "selector": "Yes"},
            {"endpoint": "contact.contact_us_fast_tracked", "reason": "harm"},
        ]
    ),
    pytest.param(
        [
            "Domestic abuse",
            "FGM",
            {"type": "form", "selector": "Yes"},
            {"endpoint": "contact.contact_us_fast_tracked", "reason": "harm"},
        ]
    ),
    pytest.param(
        [
            "Domestic abuse",
            "Leaving an abusive relationship",
            {"type": "form", "selector": "Yes"},
            {"endpoint": "contact.contact_us_fast_tracked", "reason": "harm"},
        ]
    ),
    pytest.param(
        [
            "Domestic abuse",
            "Problems with an ex-partner: children or money",
            {"type": "form", "selector": "Yes"},
            {"endpoint": "contact.contact_us_fast_tracked", "reason": "harm"},
        ]
    ),
    pytest.param(
        [
            "Domestic abuse",
            "Problems with neighbours, landlords or other people",
            {
                "endpoint": "contact.contact_us_fast_tracked",
                "reason": "more-info-required",
            },
        ]
    ),
    pytest.param(
        [
            "Children, families, relationships",
            "If there is domestic abuse in your family",
            {"type": "form", "selector": "Yes"},
            {"endpoint": "contact.contact_us_fast_tracked", "reason": "harm"},
        ]
    ),
    pytest.param(
        [
            "Children, families, relationships",
            "Problems with an ex-partner, divorce, when a relationship ends",
            {
                "endpoint": "contact.contact_us_fast_tracked",
                "reason": "more-info-required",
            },
        ]
    ),
    pytest.param(
        [
            "Children, families, relationships",
            "Child taken without your consent",
            {
                "endpoint": "contact.contact_us_fast_tracked",
                "reason": "more-info-required",
            },
        ]
    ),
    pytest.param(
        [
            "Children, families, relationships",
            "Children and social services, children in care",
            {
                "endpoint": "contact.contact_us_fast_tracked",
                "reason": "more-info-required",
            },
        ]
    ),
    pytest.param(
        [
            "Special educational needs and disability (SEND)",
            "Help with a child or young person's SEND",
            {"type": "form", "selector": "Yes"},
            {"endpoint": "contact.contact_us_fast_tracked", "reason": "harm"},
        ]
    ),
    pytest.param(
        [
            "Special educational needs and disability (SEND)",
            "SEND tribunals",
            {"type": "form", "selector": "Yes"},
            {"endpoint": "contact.contact_us_fast_tracked", "reason": "harm"},
        ]
    ),
]


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

    expected_heading = (
        "We will call you back"
        if "Call me back" in contact_answers["Select a contact option"]
        else "Your details have been submitted"
    )
    expect(page.get_by_role("heading", name=expected_heading)).to_be_visible()

    if "I will call you" in contact_answers["Select a contact option"]:
        expect(
            page.get_by_text("You can now call CLA on 0345 345 4 345.")
        ).to_be_visible()
        expect(
            page.get_by_text(
                "Your details have been submitted and an operator will call you at least once during your chosen time"
            )
        ).not_to_be_visible()
    if "Call me back" in contact_answers["Select a contact option"]:
        expect(
            page.get_by_text("You can now call CLA on 0345 345 4 345.")
        ).not_to_be_visible()
        expect(
            page.get_by_text(
                "Your details have been submitted and an operator will call you at least once during your chosen time"
            )
        ).to_be_visible()
        expect(
            page.get_by_text(
                "When a CLA operator calls, the call will come from an anonymous number."
            )
        ).to_be_visible()


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("contact_answers", contact_form_routing)
def test_postcode_field(page: Page, contact_answers: dict):
    """
    Test the contact page.
    """
    page.get_by_role("link", name="Contact us").click()

    page.get_by_label("I’d prefer to speak to someone").check()

    page.get_by_role("button", name="Continue").click()

    expect(
        page.get_by_role("heading", name="Contact Civil Legal Advice")
    ).to_be_visible()

    page.get_by_role("textbox", name="Your full name").fill("Test")

    page.get_by_role("radio", name="I will call you").click()

    page.get_by_role("textbox", name="Postcode (optional)").fill("SW1")

    page.get_by_role("button", name="Find UK Address").click()

    try:
        page.get_by_role("combobox", name="Select an address").select_option(index=1)
    except Exception:
        print("Skipping postcode select")

    page.get_by_role("button", name="Submit details").click()

    expect(
        page.get_by_role("heading", name="Your details have been submitted")
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("routes", fast_track_routing)
def test_fast_track_routing(page: Page, routes):
    expected_url = routes.pop()
    endpoint = expected_url["endpoint"]
    del expected_url["endpoint"]
    expected_url = url_for(endpoint, **expected_url, _external=True)

    page.goto(url_for("categories.index", _external=True))
    for route in routes:
        if isinstance(route, str):
            page.get_by_role("link", name=route).click()
        elif isinstance(route, dict):
            page.get_by_label(route["selector"]).click()
            page.get_by_role("button", name="Continue").click()

    assert page.url == expected_url
