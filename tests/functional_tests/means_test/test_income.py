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
            "single_person_unemployed",
            {
                "has_partner": "No",
                "Do you receive any benefits": "No",
                "Do you have any children aged": "No",
                "Do you have any dependants": "No",
                "Do you own any property?": "No",
                "Are you employed?": "No",
                "Are you self-employed?": "No",
                "Are you or your partner (if": "No",
                "Do you have any savings or": "No",
                "Do you have any valuable": "No",
            },
            {
                "heading": "Your money coming in",
                "fields": [
                    {"name": "Maintenance received"},
                    {"name": "Pension received"},
                    {"name": "Any other income"},
                ],
            },
        ),
        (
            "single_person_employed",
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
                "Do you have any valuable": "No",
            },
            {
                "heading": "Your income and tax",
                "fields": [{"name": "Wages before tax"}, {"name": "Income tax"}],
            },
        ),
        (
            "couple_both_unemployed",
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
                "Do you have any savings or": "No",
                "Do you have any valuable": "No",
            },
            {
                "heading": "You and your partner",
                "fields": [
                    {"name": "Maintenance received", "nth": 1},
                    {"name": "Pension received", "nth": 1},
                    {"name": "Any other income", "nth": 1},
                ],
            },
        ),
        (
            "couple_partner_employed",
            {
                "has_partner": "Yes",
                "Are you in a dispute with": "No",
                "Do you receive any benefits": "No",
                "Do you have any children aged": "No",
                "Do you have any dependants": "No",
                "Do you own any property?": "No",
                "Are you employed?": "Yes",
                "Is your partner employed?": "Yes",
                "Are you self-employed?": "No",
                "Is your partner self-employed?": "No",
                "Are you or your partner (if": "No",
                "Do you have any savings or": "No",
                "Do you have any valuable": "No",
            },
            {
                "heading": "You and your partner",
                "fields": [
                    {"name": "Wages before tax", "nth": 0},
                    {"name": "Income tax", "nth": 0},
                    {"name": "National Insurance", "nth": 0},
                    {"name": "Maintenance received", "nth": 0},
                    {"name": "Child Tax Credit", "nth": 0},
                    {"name": "Wages before tax", "nth": 1},
                    {"name": "Income tax", "nth": 1},
                    {"name": "National Insurance", "nth": 1},
                    {"name": "Maintenance received", "nth": 1},
                ],
            },
        ),
    ],
)
@pytest.mark.usefixtures("live_server")
def test_about_form(page: Page, scenario: str, form_inputs: dict, expected: dict):
    page.goto(url_for("means_test.about-you", _external=True))

    page.locator("#has_partner" if form_inputs["has_partner"] == "Yes" else "#has_partner-2").check()
    del form_inputs["has_partner"]

    fill_about_form(page, form_inputs)
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_role("heading", name=expected["heading"])).to_be_visible()

    for field in expected["fields"]:
        locator = page.get_by_role("group", name=field["name"])
        if "nth" in field:
            locator = locator.nth(field["nth"])
        expect(locator).to_be_visible()
