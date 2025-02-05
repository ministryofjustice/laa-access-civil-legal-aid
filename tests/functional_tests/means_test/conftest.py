from playwright.sync_api import Page
import pytest


@pytest.fixture
def navigate_to_means_test(page: Page):
    page.get_by_role("link", name="Housing, homelessness, losing your home").click()
    page.get_by_role("link", name="Homelessness").click()
    page.get_by_role("button", name="Check if you qualify financially").click()
    return page


@pytest.fixture
def complete_about_you_form(
    page: Page, about_you_answers: dict, navigate_to_means_test
):
    for question, answer in about_you_answers.items():
        form_group = page.get_by_role("group", name=question)
        if question == "Do you have a partner":
            locator = "#has_partner" if answer == "Yes" else "#has_partner-2"
            form_group.locator(locator).check()
            continue
        if question == "How many children aged 15 or under?":
            page.locator("#num_children").fill(answer)
            continue
        form_group.get_by_label(answer).first.check()
    # Submit form
    page.get_by_role("button", name="Continue").click()
    return page


@pytest.fixture
def complete_benefits_form(page: Page, benefits_answers: dict, complete_about_you_form):
    for question, answer in benefits_answers.items():
        form_group = page.get_by_role("group", name=question)
        if question == "If yes, enter the total amount you get for all your children":
            page.get_by_label("Amount").fill(answer["Amount"])
            page.get_by_label("Frequency").select_option(label=answer["Frequency"])
        elif isinstance(answer, list):
            for label in answer:
                form_group.get_by_label(label).first.check()
        else:
            form_group.get_by_label(answer).first.check()
    # Submit form
    page.get_by_role("button", name="Continue").click()

    return page
