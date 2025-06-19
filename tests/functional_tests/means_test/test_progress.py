import pytest
from playwright.sync_api import Page, expect


def fill_in_full_about_you_form(page: Page):
    # Fill in about you form
    page.locator("#has_partner").check()
    page.get_by_role("group", name="Are you in a dispute with").get_by_label(
        "No"
    ).check()
    page.get_by_role("group", name="Do you receive any benefits (").get_by_label(
        "Yes"
    ).check()
    page.get_by_role("group", name="Do you have any children aged").get_by_label(
        "No"
    ).check()
    page.get_by_role("group", name="Do you have any dependants").get_by_label(
        "No"
    ).check()
    page.get_by_role("group", name="Do you own any property?").get_by_label(
        "Yes"
    ).check()
    page.get_by_role("group", name="Are you employed?").get_by_label("Yes").check()
    page.get_by_role("group", name="Is your partner employed?").get_by_label(
        "No"
    ).check()
    page.get_by_role("group", name="Are you self-employed?").get_by_label("No").check()
    page.get_by_role("group", name="Is your partner self-employed?").get_by_label(
        "No"
    ).check()
    page.get_by_role("group", name="Are you or your partner (if").get_by_label(
        "Yes"
    ).check()
    page.get_by_role("group", name="Do you have any savings or").get_by_label(
        "Yes"
    ).check()
    page.get_by_role("group", name="Do you have any valuable").get_by_label(
        "Yes"
    ).check()
    page.get_by_role("button", name="Continue").click()


def fill_in_minimal_about_you_form(page: Page):
    page.locator("#has_partner-2").check()
    page.get_by_role("group", name="Do you receive any benefits (").get_by_label(
        "No"
    ).check()
    page.get_by_role("group", name="Do you have any children aged").get_by_label(
        "No"
    ).check()
    page.get_by_role("group", name="Do you have any dependants").get_by_label(
        "No"
    ).check()
    page.get_by_role("group", name="Do you own any property?").get_by_label(
        "No"
    ).check()
    page.get_by_role("group", name="Are you employed?").get_by_label("No").check()
    page.get_by_role("group", name="Are you self-employed?").get_by_label("No").check()
    page.get_by_role("group", name="Are you or your partner (if").get_by_label(
        "No"
    ).check()
    page.get_by_role("group", name="Do you have any savings or").get_by_label(
        "No"
    ).check()
    page.get_by_role("group", name="Do you have any valuable").get_by_label(
        "No"
    ).check()
    page.get_by_role("button", name="Continue").click()


@pytest.mark.usefixtures("live_server")
@pytest.mark.usefixtures("navigate_to_means_test")
def test_progress_component_full(page: Page):
    expect(page.get_by_text("Current page: About you")).to_be_visible()

    fill_in_full_about_you_form(page)

    expect(page.get_by_text("Current page: Which benefits")).to_be_visible()
    expect(
        page.get_by_text("Future page: You and your partner’s property")
    ).to_be_visible()
    expect(
        page.get_by_text("Future page: You and your partner’s savings")
    ).to_be_visible()
    expect(
        page.get_by_text("Future page: You and your partner’s income and tax")
    ).to_be_visible()
    expect(
        page.get_by_text("Future page: Check your answers and confirm")
    ).to_be_visible()
    expect(page.get_by_text("Future page: Contact information")).to_be_visible()

    page.get_by_role("link", name="Completed page: About you").click()
    expect(page.get_by_text("Current page: About you")).to_be_visible()


@pytest.mark.usefixtures("live_server")
@pytest.mark.usefixtures("navigate_to_means_test")
def test_progress_component_additional_benefits(page: Page):
    expect(page.get_by_text("Current page: About you")).to_be_visible()

    fill_in_full_about_you_form(page)

    expect(page.get_by_text("Current page: Which benefits")).to_be_visible()

    page.get_by_role("checkbox", name="Any other benefits").check()

    page.get_by_role("button", name="Continue").click()
    expect(
        page.get_by_text("Current page: You and your partner’s additional benefits")
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
@pytest.mark.usefixtures("navigate_to_means_test")
def test_progress_component_collapsed_steps(page: Page):
    expect(page.get_by_text("Current page: About you")).to_be_visible()

    # The three collapsed steps should be visible if we have not yet submitted the about you form
    expect(
        page.get_by_role("list")
        .filter(has_text="Current page: About you")
        .locator("div")
        .nth(1)
    ).to_be_visible()
    expect(
        page.get_by_role("list")
        .filter(has_text="Current page: About you")
        .locator("div")
        .nth(2)
    ).to_be_visible()
    expect(
        page.get_by_role("list")
        .filter(has_text="Current page: About you")
        .locator("div")
        .nth(2)
    ).to_be_visible()

    fill_in_full_about_you_form(page)

    expect(page.get_by_text("Current page: Which benefits")).to_be_visible()

    # Once we go back to the about you page the collapsed steps should no longer be shown
    page.get_by_role("link", name="Completed page: About you").click()
    expect(
        page.get_by_role("list")
        .filter(has_text="Current page: About you")
        .locator("div")
        .nth(1)
    ).not_to_be_visible()
    expect(
        page.get_by_role("list")
        .filter(has_text="Current page: About you")
        .locator("div")
        .nth(2)
    ).not_to_be_visible()
    expect(
        page.get_by_role("list")
        .filter(has_text="Current page: About you")
        .locator("div")
        .nth(2)
    ).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
@pytest.mark.usefixtures("navigate_to_means_test")
def test_progress_bar_review_answers_and_contact(page: Page):
    fill_in_minimal_about_you_form(page)
    page.get_by_role("group", name="Maintenance received").get_by_label("Amount").fill(
        "0"
    )
    page.get_by_role("group", name="Pension received").get_by_label("Amount").fill("0")
    page.get_by_role("group", name="Any other income").get_by_label("Amount").fill("0")
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_text("Current page: Check your answers")).to_be_visible()
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_text("Current page: Contact information")).to_be_visible()
