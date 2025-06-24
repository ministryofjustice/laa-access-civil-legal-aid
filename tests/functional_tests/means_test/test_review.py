import pytest

from flask import url_for
from playwright.sync_api import Page, expect
from tests.functional_tests.means_test.conftest import (
    assert_benefits_form_is_prefilled,
    assert_about_you_form_is_prefilled,
)


about_you_form_routing = [
    pytest.param(
        {
            "Do you have a partner?": "No",
            "Do you receive any benefits (including Child Benefit)?": "Yes",
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


def get_answers():
    return {
        "The problem you need help with": {
            "The problem you need help with": "Homelessness\nHelp if you’re homeless, or might be homeless in the next 2 months. This could be because of rent arrears, debt, the end of a relationship, or because you have nowhere to live."
        },
        "About you": about_you_form_routing[0].values[0].copy(),
        "Which benefits do you receive?": benefits_form_routing[0].values[0].copy(),
    }


def assert_answers(page: Page, answers):
    for title, route in answers.items():
        table = page.locator(f".govuk-summary-list[data-question='{title}']")
        for question, answer in route.items():
            if isinstance(answer, dict) and "Amount" in answer:
                answer = f"{answer['Amount']} ({answer['Frequency']})"
                if not answer.startswith("£"):
                    answer = f"£{answer}"
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
    expect(page).to_have_title("Check your answers and confirm - GOV.UK")
    # These forms were not completed and should not be on the reviews form
    expect(page.get_by_role("heading", name="Your income and tax")).not_to_be_visible()
    expect(page.get_by_role("heading", name="Your property")).not_to_be_visible()

    # This was a conditional field which was not triggered and should not be on the review form
    expect(page.get_by_text("Are you in a dispute with your partner?")).not_to_be_visible()

    # These forms WERE completed and should be on the reviews form
    expect(page.get_by_role("heading", name="About you")).to_be_visible()
    expect(page.get_by_role("heading", name="Which benefits do you receive?")).to_be_visible()

    assert_answers(page, get_answers())


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("about_you_answers", about_you_form_routing)
@pytest.mark.parametrize("benefits_answers", benefits_form_routing)
def test_reviews_page_change_benefits_answer(page: Page, complete_benefits_form):
    expect(page).to_have_title("Check your answers and confirm - GOV.UK")
    answers = get_answers()
    page.locator("a[href='/benefits#benefits']").click()
    expect(page).to_have_title("Which benefits do you receive? - GOV.UK")
    assert_benefits_form_is_prefilled(page, answers["Which benefits do you receive?"])

    # Remove 'Universal Credit' as a selected benefit
    page.get_by_label("Universal Credit").first.uncheck()
    page.get_by_role("button", name="Continue").click()
    expect(page).to_have_title("Check your answers and confirm - GOV.UK")

    benefits_answers = answers["Which benefits do you receive?"]["Which benefits do you receive?"][:]
    # Remove universal credit from the list of answers
    benefits_answers = [item for item in benefits_answers if item not in ["Universal Credit"]]
    answers["Which benefits do you receive?"]["Which benefits do you receive?"] = benefits_answers
    assert_answers(page, answers)


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("about_you_answers", about_you_form_routing)
@pytest.mark.parametrize("benefits_answers", benefits_form_routing)
def test_reviews_page_change_sub_category(page: Page, complete_benefits_form):
    answers = get_answers()
    expect(page).to_have_title("Check your answers and confirm - GOV.UK")
    page.locator(".govuk-summary-list__actions a[href='/find-your-problem']").click()
    page.get_by_text("Housing, homelessness, losing your home").click()
    page.get_by_text("Eviction, told to leave your home").click()
    expect(page).to_have_title(
        "Legal aid is available for this type of problem - Check if you can get legal aid – GOV.UK"
    )

    page.locator("a[href='/about-you']").click()
    expect(page).to_have_title("About you - GOV.UK")
    assert_about_you_form_is_prefilled(page, answers["About you"])
    page.get_by_role("button", name="Continue").click()

    expect(page).to_have_title("Which benefits do you receive? - GOV.UK")
    assert_benefits_form_is_prefilled(page, answers["Which benefits do you receive?"])
    page.get_by_role("button", name="Continue").click()

    expect(page).to_have_title("Check your answers and confirm - GOV.UK")

    answers["The problem you need help with"]["The problem you need help with"] = (
        "Eviction, told to leave your home\nLandlord has told you to leave or is trying to force you to leave. Includes if you’ve got a Section 21 or a possession order."
    )
    assert_answers(page, answers)


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("about_you_answers", about_you_form_routing)
@pytest.mark.parametrize("benefits_answers", benefits_form_routing)
def test_reviews_page_change_category(page: Page, complete_benefits_form):
    expect(page).to_have_title("Check your answers and confirm - GOV.UK")
    page.goto(url_for("categories.index", _external=True))
    page.get_by_text("Discrimination").click()
    page.get_by_label("Work - including colleagues, employer or employment agency").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_label("Race, colour, ethnicity, nationality").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_label("No").check()
    page.get_by_role("button", name="Continue").click()
    expect(page).to_have_title(
        "Legal aid is available for this type of problem - Check if you can get legal aid – GOV.UK"
    )
    page.goto(url_for("means_test.review", _external=True))
    answers = get_answers()
    answers["The problem you need help with"].update(
        {
            "The problem you need help with": "Discrimination",
            "Where did the discrimination happen?": "Work - including colleagues, employer or employment agency",
            "Why were you discriminated against?": "Race, colour, ethnicity, nationality",
            "Are you under 18?": "No",
        }
    )
    assert_answers(page, answers)


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("about_you_answers", about_you_form_routing)
@pytest.mark.parametrize("benefits_answers", benefits_form_routing)
def test_change_answer_skip_means(page: Page, complete_benefits_form):
    expect(page).to_have_title("Check your answers and confirm - GOV.UK")
    page.goto(url_for("categories.domestic_abuse.landing", _external=True))
    page.get_by_text("Problems with neighbours, landlords or other people").click()
    page.get_by_role("heading", name="Contact us page")


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("about_you_answers", about_you_form_routing)
@pytest.mark.parametrize("benefits_answers", benefits_form_routing)
def test_change_answer_out_of_scope_problem(page: Page, complete_benefits_form):
    expect(page).to_have_title("Check your answers and confirm - GOV.UK")
    page.goto(url_for("categories.housing.landing", _external=True))
    page.get_by_text("Next steps to get help").click()
    page.get_by_role("heading", name="Legal aid doesn’t cover all types of problem")


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("about_you_answers", about_you_form_routing)
@pytest.mark.parametrize("benefits_answers", benefits_form_routing)
def test_change_answer_nolonger_passported(page: Page, complete_benefits_form):
    # Change from passported means to non-passported
    answers = get_answers()

    expect(page).to_have_title("Check your answers and confirm - GOV.UK")
    page.goto(url_for("means_test.about-you", _external=True))
    assert_about_you_form_is_prefilled(page, answers["About you"])
    # You no longer receive benefits
    locator = page.get_by_text("Do you receive any benefits (including Child Benefit)?").locator("..")
    locator.get_by_label("No").click()
    page.get_by_role("button", name="Continue").click()

    expect(page).to_have_title("Your money coming in - GOV.UK")
    answers["Your money coming in"] = {
        "Maintenance received": {
            "Amount": "1420.56",
            "Frequency": "per month",
            "prefix": "maintenance_received",
        },
        "Pension received": {
            "Amount": "8.01",
            "Frequency": "per month",
            "prefix": "pension",
        },
        "Any other income": {
            "Amount": "10.00",
            "Frequency": "per month",
            "prefix": "other_income",
        },
    }
    for field in answers["Your money coming in"].values():
        page.locator(f"#{field['prefix']}-value").scroll_into_view_if_needed()
        page.locator(f"#{field['prefix']}-value").fill(field["Amount"])
        page.locator(f"#{field['prefix']}-interval").select_option(field["Frequency"])

    page.get_by_role("button", name="Continue").click()

    answers["Your outgoings"] = {
        "Rent": {"Amount": "50.99", "Frequency": "per week", "prefix": "rent"},
        "Maintenance": {
            "Amount": "18.28",
            "Frequency": "per month",
            "prefix": "maintenance",
        },
        "Childcare": {
            "Amount": "12.34",
            "Frequency": "per month",
            "prefix": "childcare",
        },
    }
    for field in answers["Your outgoings"].values():
        page.locator(f"#{field['prefix']}-value").scroll_into_view_if_needed()
        page.locator(f"#{field['prefix']}-value").fill(field["Amount"])
        page.locator(f"#{field['prefix']}-interval").select_option(field["Frequency"])

    answers["Your outgoings"]["Monthly Income Contribution Order"] = "£50.00"
    page.get_by_label("Monthly Income Contribution Order").fill("50.00")
    page.get_by_role("button", name="Review your answers").click()
    # No longer on benefits
    del answers["Which benefits do you receive?"]
    del answers["About you"]["Do you receive any benefits (including Child Benefit)?"]
    assert_answers(page, answers)

    expect(page.get_by_text("Which benefits do you receive?")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_review_page_failed_access_without_completing_means(page: Page, request):
    """Attempt to access review page after completing the scope answers only but not the means test forms.."""
    page.goto(url_for("means_test.review", _external=True))
    assert page.title() == "You’ve reached the end of this service"

    request.getfixturevalue("navigate_to_means_test")
    page.goto(url_for("means_test.review", _external=True))
    assert page.title() == "You’ve reached the end of this service"


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize(
    "about_you_answers",
    [
        {
            "Do you receive any benefits (including Child Benefit)?": "Yes",
        }
    ],
)
def test_review_page_failed_access_incomplete_means(page: Page, complete_about_you_form):
    """Attempt to access review page without completing all means forms."""
    page.goto(url_for("means_test.review", _external=True))
    assert page.title() == "You’ve reached the end of this service"


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize(
    "benefits_answers",
    [
        {
            "Which benefits do you receive?": [
                "Universal Credit",
            ],
        }
    ],
)
@pytest.mark.parametrize(
    "about_you_answers",
    [
        {
            "Do you receive any benefits (including Child Benefit)?": "Yes",
        }
    ],
)
def test_review_page_success_access_completed_means(page: Page, complete_benefits_form):
    """Attempt to access review page without completing all means forms."""
    page.goto(url_for("means_test.review", _external=True))
    assert page.title() == "Check your answers and confirm - GOV.UK"
