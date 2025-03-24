from playwright.sync_api import Page, expect
import pytest

about_you_form_routing = [
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
    ),
]


@pytest.fixture
def navigate_to_property(page: Page, answers: dict, navigate_to_means_test):
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
    return page


property_form_routing = [
    pytest.param(
        {
            "Is this property your main home?": ["Yes", "radio"],
            "Does anyone else own a share of the property?": ["No", "radio"],
            "How much is the property worth?": ["300000", "input"],
            "How much is left to pay on the mortgage?": ["200000", "input"],
            "How much was your monthly mortgage repayment last month?": [
                "1000",
                "input",
            ],
            "Do you rent out any part of this property?": ["Yes", "radio"],
            "Amount": ["500", "input"],
            "Frequency": ["per month", "select"],
            "Is your share of the property in dispute?": ["No", "radio"],
        },
    ),
    pytest.param(
        {
            "Is this property your main home?": ["Yes", "radio"],
            "Does anyone else own a share of the property?": ["No", "radio"],
            "How much is the property worth?": ["300000", "input"],
            "How much is left to pay on the mortgage?": ["200000", "input"],
            "How much was your monthly mortgage repayment last month?": [
                "1000",
                "input",
            ],
            "Do you rent out any part of this property?": ["No", "radio"],
            "Is your share of the property in dispute?": ["No", "radio"],
        },
    ),
]

multi_property_form_routing = [
    pytest.param(
        {
            "Is this property your main home?": ["No", "radio"],
            "Does anyone else own a share of the property?": ["No", "radio"],
            "How much is the property worth?": ["3000", "input"],
            "How much is left to pay on the mortgage?": ["200000", "input"],
            "How much was your monthly mortgage repayment last month?": [
                "1000",
                "input",
            ],
            "Do you rent out any part of this property?": ["Yes", "radio"],
            "Amount": ["50", "input"],
            "Frequency": ["per month", "select"],
            "Is your share of the property in dispute?": ["No", "radio"],
        },
    ),
]

main_property_form_routing = [
    pytest.param(
        {
            "Is this property your main home?": ["Yes", "radio"],
            "Does anyone else own a share of the property?": ["No", "radio"],
            "How much is the property worth?": ["300000", "input"],
            "How much is left to pay on the mortgage?": ["200000", "input"],
            "How much was your monthly mortgage repayment last month?": [
                "1000",
                "input",
            ],
            "Do you rent out any part of this property?": ["Yes", "radio"],
            "Amount": ["500", "input"],
            "Frequency": ["per month", "select"],
            "Is your share of the property in dispute?": ["No", "radio"],
        },
    ),
]


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("answers", about_you_form_routing)
@pytest.mark.parametrize("property_answers", property_form_routing)
def test_property_routing(page: Page, property_answers: dict, navigate_to_property):
    """
    Test the property form routing.

    Args:
        page: Playwright page fixture
        property_answers: List of labels to update on the page
        navigate_to_property: Fixture to reach the property means test page
    """
    expect(page.get_by_role("heading", name="Your Property")).to_be_visible()
    for question, answer in property_answers.items():
        form_group = page.get_by_role("group", name=question)
        if answer[1] == "radio":
            form_group.get_by_label(answer[0]).check()
        elif answer[1] == "input":
            page.get_by_label(question).fill(answer[0])
        elif answer[1] == "select":
            page.get_by_label(question).select_option(answer[0])
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_role("heading", name="Your money coming in")).to_be_visible()


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("answers", about_you_form_routing)
@pytest.mark.parametrize("property_answers", multi_property_form_routing)
def test_multi_property_routing(
    page: Page, property_answers: dict, navigate_to_property
):
    """
    Test the property form routing.

    Args:
        page: Playwright page fixture
        property_answers: List of labels to update on the page
        navigate_to_property: Fixture to reach the property means test page
    """
    expect(page.get_by_role("heading", name="Your Property")).to_be_visible()
    for question, answer in property_answers.items():
        form_group = page.get_by_role("group", name=question)
        if answer[1] == "radio":
            form_group.get_by_label(answer[0]).check()
        elif answer[1] == "input":
            page.get_by_label(question).fill(answer[0])
        elif answer[1] == "select":
            page.get_by_label(question).select_option(answer[0])
    page.get_by_role("button", name="Add another property").click()
    expect(page.get_by_text("Property 1")).to_be_visible()
    expect(page.get_by_text("Property 2")).to_be_visible()
    for question, answer in property_answers.items():
        property_form_group = page.get_by_role("group", name="Property 2")
        form_group = property_form_group.get_by_role("group", name=question)
        if answer[1] == "radio":
            form_group.get_by_label(answer[0]).check()
        elif answer[1] == "input":
            property_form_group.get_by_label(question).fill(answer[0])
        elif answer[1] == "select":
            property_form_group.get_by_label(question).select_option(answer[0])
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_role("heading", name="Your money coming in")).to_be_visible()


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("answers", about_you_form_routing)
@pytest.mark.parametrize("property_answers", main_property_form_routing)
def test_multi_main_property(page: Page, property_answers: dict, navigate_to_property):
    """
    Test the property form routing.

    Args:
        page: Playwright page fixture
        property_answers: List of labels to update on the page
        navigate_to_property: Fixture to reach the property means test page
    """
    expect(page.get_by_role("heading", name="Your Property")).to_be_visible()
    for question, answer in property_answers.items():
        form_group = page.get_by_role("group", name=question)
        if answer[1] == "radio":
            form_group.get_by_label(answer[0]).check()
        elif answer[1] == "input":
            page.get_by_label(question).fill(answer[0])
        elif answer[1] == "select":
            page.get_by_label(question).select_option(answer[0])
    page.get_by_role("button", name="Add another property").click()
    expect(page.get_by_text("Property 1")).to_be_visible()
    expect(page.get_by_text("Property 2")).to_be_visible()
    for question, answer in property_answers.items():
        property_form_group = page.get_by_role("group", name="Property 2")
        form_group = property_form_group.get_by_role("group", name=question)
        if answer[1] == "radio":
            form_group.get_by_label(answer[0]).check()
        elif answer[1] == "input":
            property_form_group.get_by_label(question).fill(answer[0])
        elif answer[1] == "select":
            property_form_group.get_by_label(question).select_option(answer[0])
    page.get_by_role("button", name="Continue").click()
    expect(
        page.get_by_role("link", name="You can only have 1 main property")
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("answers", about_you_form_routing)
def test_property_page_errors(page: Page, navigate_to_property):
    """
    Test the property form routing.

    Args:
        page: Playwright page fixture
        navigate_to_property: Fixture to reach the property means test pa
    """
    expect(page.get_by_role("heading", name="Your Property")).to_be_visible()
    page.get_by_role("button", name="Continue").click()

    # Check that all error messages are visible
    expect(
        page.get_by_role("link", name="Tell us whether this is your main home")
    ).to_be_visible()
    expect(
        page.get_by_role(
            "link", name="Tell us whether anyone else owns a share of this property"
        )
    ).to_be_visible()
    expect(
        page.get_by_role("link", name="Tell us the approximate value of this property")
    ).to_be_visible()
    expect(
        page.get_by_role("link", name="Tell us how much is left to pay on the mortgage")
    ).to_be_visible()
    expect(
        page.get_by_role("link", name="Enter your mortgage repayment for last month")
    ).to_be_visible()
    expect(
        page.get_by_role(
            "link", name="Tell us whether you rent out some of this property"
        )
    ).to_be_visible()
    expect(
        page.get_by_role("link", name="Tell us whether this property is in dispute")
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("answers", about_you_form_routing)
def test_multiple_properties(page: Page, navigate_to_property):
    """
    Test adding and removing all properties
    """
    expect(page.get_by_role("heading", name="Your Property")).to_be_visible()
    expect(
        page.get_by_text("Property 1")
    ).not_to_be_visible()  # The "Property 1" heading should only be displayed when there are multiple properties
    expect(page.get_by_text("Property 2")).not_to_be_visible()
    expect(page.get_by_text("Property 3")).not_to_be_visible()

    page.get_by_role("button", name="Add another property").click()
    expect(page.get_by_text("Property 1")).to_be_visible()
    expect(page.get_by_text("Property 2")).to_be_visible()
    expect(page.get_by_text("Property 3")).not_to_be_visible()

    page.get_by_role("button", name="Add another property").click()
    expect(page.get_by_text("Property 1")).to_be_visible()
    expect(page.get_by_text("Property 2")).to_be_visible()
    expect(page.get_by_text("Property 3")).to_be_visible()

    page.get_by_role("group", name="Property 3").get_by_label(
        "How much is the property"
    ).fill("3000")

    page.locator('button[name="remove-property-2"]').click()
    expect(page.get_by_text("Property 1")).to_be_visible()
    expect(page.get_by_text("Property 2")).to_be_visible()
    expect(page.get_by_text("Property 3")).not_to_be_visible()

    expect(
        page.get_by_role("group", name="Property 2").get_by_label(
            "How much is the property"
        )
    ).to_have_value("3000")

    page.locator('button[name="remove-property-2"]').click()
    expect(page.get_by_text("Property 1")).not_to_be_visible()
    expect(page.get_by_text("Property 2")).not_to_be_visible()
    expect(page.get_by_text("Property 3")).not_to_be_visible()
