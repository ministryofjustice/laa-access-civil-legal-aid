import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def fill_about_form(page: Page, questions: dict) -> None:
    for question, answer in questions.items():
        page.get_by_role("group", name=question).get_by_label(answer).check()


@pytest.mark.parametrize(
    "scenario,form_inputs,expected",
    [
        (
            "single_person_savings",
            {
                "has_partner": "No",
                "Do you receive any benefits": "No",
                "Do you have any children aged": "No",
                "Do you have any dependants": "No",
                "Do you own any property?": "No",
                "Are you employed?": "No",
                "Are you self-employed?": "No",
                "Are you or your partner (if": "No",
                "Do you have any savings or": "Yes",
                "Do you have any valuable": "No",
            },
            {
                "heading": "Your savings",
                "fields": [
                    {"name": "Savings"},
                    {"name": "Investments"},
                ],
            },
        ),
        (
            "single_person_valuables",
            {
                "has_partner": "No",
                "Do you receive any benefits": "No",
                "Do you have any children aged": "No",
                "Do you have any dependants": "No",
                "Do you own any property?": "No",
                "Are you employed?": "Yes",
                "Are you self-employed?": "No",
                "Are you or your partner (if": "No",
                "Do you have any savings or": "No",
                "Do you have any valuable": "Yes",
            },
            {
                "heading": "Your savings",
                "fields": [{"name": "Total value of items worth over"}],
            },
        ),
        (
            "couple_savings_and_investments",
            {
                "has_partner": "Yes",
                "Are you in a dispute with": "No",
                "Do you receive any benefits": "No",
                "Do you have any children aged": "No",
                "Do you have any dependants": "No",
                "Do you own any property?": "No",
                "Are you employed?": "No",
                "Is your partner employed?": "No",
                "Are you self-employed?": "No",
                "Is your partner self-employed?": "No",
                "Are you or your partner (if": "No",
                "Do you have any savings or": "Yes",
                "Do you have any valuable": "Yes",
            },
            {
                "heading": "You and your partner’s savings",
                "fields": [
                    {"name": "Savings"},
                    {"name": "Investments"},
                    {"name": "Total value of items worth over"},
                ],
            },
        ),
    ],
)
@pytest.mark.usefixtures("live_server")
def test_savings_form(page: Page, scenario: str, form_inputs: dict, expected: dict):
    page.goto(url_for("means_test.about-you", _external=True))

    page.locator(
        "#has_partner" if form_inputs["has_partner"] == "Yes" else "#has_partner-2"
    ).check()
    del form_inputs["has_partner"]

    fill_about_form(page, form_inputs)
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_text(expected["heading"])).to_be_visible()

    for field in expected["fields"]:
        locator = page.get_by_label(field["name"])
        if "nth" in field:
            locator = locator.nth(field["nth"])
        expect(locator).to_be_visible()
