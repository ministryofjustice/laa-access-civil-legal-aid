from playwright.sync_api import Page, expect
import pytest

about_you_form_routing = [
    pytest.param(
        {
            "Do you have a partner": "No",
            "Do you receive any benefits": "No",
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
    ),
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
        "Which benefits do you receive?",
        id="benefits_route",
    ),
    pytest.param(
        {
            "Do you have a partner": "No",
            "Do you receive any benefits": "No",
            "Do you have any children aged 15 or under?": "No",
            "Do you have any dependants aged 16 or over?": "No",
            "Do you own any property?": "Yes",
            "Are you employed?": "No",
            "Are you self-employed?": "No",
            "Are you or your partner (if you have one) aged 60 or over?": "No",
            "Do you have any savings or investments?": "No",
            "Do you have any valuable items worth over £500 each?": "No",
        },
        "Your property",
        id="property_route",
    ),
]


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("answers,route_to", about_you_form_routing)
def test_about_you_routing(page: Page, answers: dict, route_to: str):
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

    expect(page.get_by_text(route_to)).to_have_count(
        2
    )  # This checks for a count of two as the text also exists in the progress bar


@pytest.mark.usefixtures("live_server")
def test_error_messages(page: Page):
    page.get_by_role("link", name="Housing, homelessness, losing your home").click()
    page.get_by_role("link", name="Homelessness").click()
    page.get_by_role("button", name="Check if you qualify financially").click()

    # Submit form
    page.get_by_role("button", name="Continue").click()

    # Check that all error messages are visible
    expect(
        page.get_by_role("link", name="Tell us whether you have a partner")
    ).to_be_visible()
    expect(
        page.get_by_role("link", name="Tell us whether you receive benefits")
    ).to_be_visible()
    expect(
        page.get_by_role(
            "link", name="Tell us whether you have any children aged 15 or under"
        )
    ).to_be_visible()
    expect(
        page.get_by_role(
            "link", name="Tell us whether you have any dependants aged 16 or over"
        )
    ).to_be_visible()
    expect(
        page.get_by_role("link", name="Tell us if you own any properties")
    ).to_be_visible()
    expect(page.get_by_role("link", name="Tell us if you are employed")).to_be_visible()
    expect(
        page.get_by_role("link", name="Tell us if you are self-employed")
    ).to_be_visible()
    expect(
        page.get_by_role(
            "link", name="Tell us if you or your partner are aged 60 or over"
        )
    ).to_be_visible()
    expect(
        page.get_by_role("link", name="Tell us whether you have savings or investments")
    ).to_be_visible()
    expect(
        page.get_by_role(
            "link", name="Tell us if you have any valuable items worth over £500 each"
        )
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_conditional_fields(page: Page):
    page.get_by_role("link", name="Housing, homelessness, losing").click()
    page.get_by_role("link", name="Homelessness").click()
    page.get_by_role("button", name="Check if you qualify").click()

    expect(
        page.get_by_role("group", name="Are you in a dispute with")
    ).not_to_be_visible()
    page.locator("#has_partner").check()
    expect(page.get_by_role("group", name="Are you in a dispute with")).to_be_visible()

    expect(page.locator("#conditional-have_children div")).not_to_be_visible()
    page.get_by_role("group", name="Do you have any children aged").get_by_label(
        "Yes"
    ).check()
    expect(page.locator("#conditional-have_children div")).to_be_visible()

    expect(page.locator("#conditional-have_dependants div")).not_to_be_visible()
    page.get_by_role("group", name="Do you have any dependants").get_by_label(
        "Yes"
    ).check()
    expect(page.locator("#conditional-have_dependants div")).to_be_visible()
