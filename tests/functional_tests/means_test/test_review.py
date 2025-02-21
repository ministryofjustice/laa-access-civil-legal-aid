import pytest
from flask import url_for
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
        id="benefits",
    )
]

ANSWERS = {
    "The problem you need help with": {
        "The problem you need help with": "Homelessness\nHelp if you’re homeless, or might be homeless in the next 2 months. This could be because of rent arrears, debt, the end of a relationship, or because you have nowhere to live."
    },
    "About you": about_you_form_routing[0].values[0],
    "Which benefits do you receive?": benefits_form_routing[0].values[0],
}


def assert_answers(page, answers):
    for title, route in answers.items():
        table = page.locator(f".govuk-summary-list[data-question='{title}']")
        for question, answer in route.items():
            if (
                question
                == "If yes, enter the total amount you get for all your children"
            ):
                answer = "£500.89 (4 weekly)"
            if question == "How many children aged 15 or under?":
                question = "How many?"
            question_cell = table.get_by_text(question)
            expect(question_cell).to_be_visible()
            if isinstance(answer, list):
                answer = "\n".join(answer)
            expect(question_cell.locator(" + dd")).to_have_text(answer)


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("about_you_answers", about_you_form_routing)
@pytest.mark.parametrize("benefits_answers", benefits_form_routing)
def test_reviews_page(page: Page, complete_benefits_form):
    expect(page).to_have_title("Review your answers - GOV.UK")
    # These forms were not completed and should not be on the reviews form
    expect(page.get_by_role("heading", name="Your income and tax")).not_to_be_visible()
    expect(page.get_by_role("heading", name="Your property")).not_to_be_visible()

    # This was a conditional field which was not triggered and should not be on the review form
    expect(
        page.get_by_text("Are you in a dispute with your partner?")
    ).not_to_be_visible()

    # These forms WERE completed and should be on the reviews form
    expect(page.get_by_role("heading", name="About you")).to_be_visible()
    expect(
        page.get_by_role("heading", name="Which benefits do you receive?")
    ).to_be_visible()

    assert_answers(page, ANSWERS)


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("about_you_answers", about_you_form_routing)
@pytest.mark.parametrize("benefits_answers", benefits_form_routing)
def test_reviews_page_change_benefits_answer(page: Page, complete_benefits_form):
    expect(page).to_have_title("Review your answers - GOV.UK")
    page.locator("a[href='/benefits#benefits']").click()
    expect(page).to_have_title("Which benefits do you receive? - GOV.UK")
    page.get_by_label("Universal Credit").first.uncheck()
    page.get_by_role("button", name="Continue").click()
    expect(page).to_have_title("Review your answers - GOV.UK")

    answers = ANSWERS.copy()
    benefits_answers = answers["Which benefits do you receive?"][
        "Which benefits do you receive?"
    ][:]
    # Remove universal credit from the list of answers
    benefits_answers = [
        item for item in benefits_answers if item not in ["Universal Credit"]
    ]
    answers["Which benefits do you receive?"]["Which benefits do you receive?"] = (
        benefits_answers
    )
    assert_answers(page, answers)


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("about_you_answers", about_you_form_routing)
@pytest.mark.parametrize("benefits_answers", benefits_form_routing)
def test_reviews_page_change_sub_category(page: Page, complete_benefits_form):
    expect(page).to_have_title("Review your answers - GOV.UK")
    page.locator(".govuk-summary-list__actions a[href='/housing/']").click()
    page.get_by_text("Eviction, told to leave your home").click()
    expect(page).to_have_title(
        "Legal aid is available for this type of problem - Access Civil Legal Aid – GOV.UK"
    )
    page.locator("a[href='/about-you']").click()
    expect(page).to_have_title("About you - GOV.UK")
    page.get_by_role("button", name="Continue").click()
    expect(page).to_have_title("Which benefits do you receive? - GOV.UK")
    page.get_by_role("button", name="Continue").click()
    expect(page).to_have_title("Review your answers - GOV.UK")
    answers = ANSWERS.copy()
    answers["The problem you need help with"]["The problem you need help with"] = (
        "Eviction, told to leave your home\nLandlord has told you to leave or is trying to force you to leave. Includes if you’ve got a Section 21 or a possession order."
    )
    assert_answers(page, answers)


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("about_you_answers", about_you_form_routing)
@pytest.mark.parametrize("benefits_answers", benefits_form_routing)
def test_reviews_page_change_category(page: Page, complete_benefits_form):
    expect(page).to_have_title("Review your answers - GOV.UK")
    page.locator(".govuk-header__link--homepage[href='/']").click()
    page.get_by_text("Discrimination").click()
    page.get_by_label(
        "Work - including colleagues, employer or employment agency"
    ).check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_label("Race, colour, ethnicity, nationality").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_label("No").check()
    page.get_by_role("button", name="Continue").click()
    expect(page).to_have_title(
        "Legal aid is available for this type of problem - Access Civil Legal Aid – GOV.UK"
    )
    page.goto(url_for("means_test.review", _external=True))
    answers = ANSWERS.copy()
    answers["The problem you need help with"].update(
        {
            "The problem you need help with": "Discrimination",
            "Where did the discrimination happen?": "Work - including colleagues, employer or employment agency",
            "Why were you discriminated against?": "Race, colour, ethnicity, nationality",
            "Are you under 18?": "No",
        }
    )
    assert_answers(page, answers)

    import time

    time.sleep(10)
    # page.locator(".govuk-summary-list__actions a[href='/housing/']").click()
    # page.get_by_text("Eviction, told to leave your home").click()
    # expect(page).to_have_title("Legal aid is available for this type of problem - Access Civil Legal Aid – GOV.UK")
    # page.locator("a[href='/about-you']").click()
    # expect(page).to_have_title("About you - GOV.UK")
    # page.get_by_role("button", name="Continue").click()
    # expect(page).to_have_title("Which benefits do you receive? - GOV.UK")
    # page.get_by_role("button", name="Continue").click()
    # expect(page).to_have_title("Review your answers - GOV.UK")
    # answers = ANSWERS.copy()
    # answers["The problem you need help with"]["The problem you need help with"] = "Eviction, told to leave your home\nLandlord has told you to leave or is trying to force you to leave. Includes if you’ve got a Section 21 or a possession order."
    # assert_answers(page, answers)
