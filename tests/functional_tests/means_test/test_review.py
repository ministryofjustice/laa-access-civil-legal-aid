import pytest
from playwright.sync_api import Page, expect


about_you_form_routing = [
    pytest.param(
        {
            "Do you have a partner": "No",
            "Do you receive any benefits": "Yes",
            "Do you have any children aged 15 or under?": "Yes",
            "How many children aged 15 or under?": "1",
            "Do you have any dependants aged 16 or over?": "No",
            "Do you own any property?": "No",
            "Are you employed?": "No",
            "Are you self-employed?": "No",
            "Are you or your partner (if you have one) aged 60 or over?": "No",
            "Do you have any savings or investments?": "No",
            "Do you have any valuable items worth over £500 each?": "No",
        },
        id="about_you",
    )
]

benefits_form_routing = [
    pytest.param(
        {
            "Which benefits do you receive?": [
                "Child Benefit",
                "Guarantee Credit",
                "Income Support",
                "Income-based Jobseeker's Allowance",
                "Income-related Employment and Support Allowance",
                "Universal Credit",
            ],
            "If yes, enter the total amount you get for all your children": {
                "Amount": "500.89",
                "Frequency": "4 weekly",
            },
        },
        id="about_you",
    )
]

routing = {
    "About you": about_you_form_routing[0].values[0],
    "Which benefits do you receive?": benefits_form_routing[0].values[0],
}


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("about_you_answers", about_you_form_routing)
@pytest.mark.parametrize("benefits_answers", benefits_form_routing)
def test_reviews_page(page: Page, complete_benefits_form, about_you_answers):
    expect(page).to_have_title("Review your answers - GOV.UK")
    # These forms were not completed and should not be on the reviews form
    expect(page.get_by_role("heading", name="Your income and tax")).not_to_be_visible()
    expect(page.get_by_role("heading", name="Your property")).not_to_be_visible()

    # This was a conditional field which was not triggered and should not be on the review form
    expect(
        page.get_by_text("Are you in a dispute with your partner?")
    ).not_to_be_visible()
    expect(
        page.get_by_text("Are you in a dispute with your partner?")
    ).not_to_be_visible()

    # These forms WERE completed and should be on the reviews form
    expect(page.get_by_role("heading", name="About you")).to_be_visible()
    expect(
        page.get_by_role("heading", name="Which benefits do you receive?")
    ).to_be_visible()

    for title, route in routing.items():
        table = page.locator(f".govuk-summary-list[data-form='{title}']")
        for question, answer in route.items():
            if (
                question
                == "If yes, enter the total amount you get for all your children"
            ):
                answer = "£500.89 every 4 weekly"
            if question == "How many children aged 15 or under?":
                question = "How many?"
            question_cell = table.get_by_text(question)
            expect(question_cell).to_be_visible()
            if isinstance(answer, list):
                answer = "\n".join(answer)
            expect(question_cell.locator(" + dd")).to_have_text(answer)
