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
    ),
]

about_you_form_routing_childcare = [
    pytest.param(
        {
            "Do you have a partner": "No",
            "Do you receive any benefits": "No",
            "Do you have any children aged 15 or under?": "Yes",
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
def navigate_to_income(page: Page, answers: dict, navigate_to_means_test):
    expect(page.get_by_text("About You")).to_be_visible()
    for question, answer in answers.items():
        form_group = page.get_by_role("group", name=question)
        if question == "Do you have a partner":
            locator = "#has_partner" if answer == "Yes" else "#has_partner-2"
            form_group.locator(locator).check()
            continue
        form_group.get_by_label(answer).first.check()
        if question == "Do you have any children aged 15 or under?" and answer == "Yes":
            page.get_by_role("textbox", name="How many?").fill("1")
            continue
    # Submit form
    page.get_by_role("button", name="Continue").click()
    return page


@pytest.fixture
def navigate_to_outgoings(page: Page, navigate_to_income):
    expect(page.get_by_text("Your money coming in")).to_be_visible()
    amount_inputs = page.get_by_label("Amount")
    frequency_inputs = page.get_by_label("Frequency")

    amount_inputs.nth(0).fill("500")
    frequency_inputs.nth(0).select_option("per_month")
    amount_inputs.nth(1).fill("500")
    frequency_inputs.nth(1).select_option("per_month")
    amount_inputs.nth(2).fill("500")
    frequency_inputs.nth(2).select_option("per_month")

    page.get_by_role("button", name="Continue").click()


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("answers", about_you_form_routing)
def test_outgoings_routing(page: Page, navigate_to_outgoings):
    """
    Test the outgoings form routing.

    Args:
        page: Playwright page fixture
        navigate_to_outgoings: Fixture to reach the outgoings means test page
    """
    expect(page.get_by_text("Your outgoings")).to_be_visible()

    page.get_by_role("group", name="Rent").get_by_label("Amount").fill("500")
    page.get_by_role("group", name="Rent").get_by_label("Frequency").select_option(
        "per_month"
    )
    page.get_by_role("group", name="Maintenance").get_by_label("Amount").fill("500")
    page.get_by_role("group", name="Maintenance").get_by_label(
        "Frequency"
    ).select_option("per_month")
    page.get_by_role("textbox", name="Monthly Income Contribution").fill("500")

    page.get_by_role("button", name="Review your answers").click()
    expect(page.get_by_text("Review your answers")).to_be_visible()


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("answers", about_you_form_routing_childcare)
def test_outgoings_childcare(page: Page, navigate_to_outgoings):
    """
    Test the outgoings form childcare field.

    Args:
        page: Playwright page fixture
        navigate_to_outgoings: Fixture to reach the outgoings means test page
    """
    expect(page.get_by_text("Your outgoings")).to_be_visible()

    page.get_by_role("group", name="Rent").get_by_label("Amount").fill("500")
    page.get_by_role("group", name="Rent").get_by_label("Frequency").select_option(
        "per_month"
    )
    page.get_by_role("group", name="Maintenance").get_by_label("Amount").fill("500")
    page.get_by_role("group", name="Maintenance").get_by_label(
        "Frequency"
    ).select_option("per_month")
    page.get_by_role("textbox", name="Monthly Income Contribution").fill("500")
    page.get_by_role("group", name="Childcare").get_by_label("Amount").fill("500")
    page.get_by_role("group", name="Childcare").get_by_label("Frequency").select_option(
        "per_month"
    )

    page.get_by_role("button", name="Review your answers").click()
    expect(page.get_by_text("Review your answers")).to_be_visible()
