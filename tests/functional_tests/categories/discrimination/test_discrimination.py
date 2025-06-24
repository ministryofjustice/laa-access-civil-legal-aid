from playwright.sync_api import Page, expect
import pytest

where_form_routing = [
    pytest.param(
        ["Work - including colleagues,"],
        "Why were you discriminated against",
        id="single_answer",
    ),
    pytest.param(
        ["Work - including colleagues,", "School, college, university"],
        "Why were you discriminated against",
        id="multiple_answers",
    ),
    pytest.param(["not sure"], "Why were you discriminated against", id="not_sure"),
    pytest.param(
        ["Health or care", "not sure"],
        "Why were you discriminated against",
        id="not_sure_and_answer",
    ),
]


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("selections,expected_heading", where_form_routing)
def test_discrimination_where(page: Page, selections: list, expected_heading: str):
    """
    Test the discrimination form with different combinations of selections.

    Args:
        page: Playwright page fixture
        selections: List of labels to check
        expected_heading: Text expected to be visible after submission
    """
    page.get_by_role("link", name="Discrimination").click()

    # Check all selected options
    for selection in selections:
        page.get_by_label(selection).check()

    # Submit form
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_text(expected_heading)).to_be_visible()


why_form_routing = [
    pytest.param(
        ["Race, colour, ethnicity, nationality"],
        "Are you under 18?",
        id="single_answer",
    ),
    pytest.param(
        [
            "Disability, health condition, mental health condition",
            "Religion, belief, lack of religion",
        ],
        "Are you under 18?",
        id="multiple_answers",
    ),
    pytest.param(["None of these"], "Sorry, you’re not likely to get legal aid", id="not_sure"),
]


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("selections,expected_heading", why_form_routing)
def test_discrimination_why(page: Page, selections: list, expected_heading: str):
    """
    Test the discrimination form with different combinations of selections.

    Args:
        page: Playwright page fixture
        selections: List of labels to check
        expected_heading: Text expected to be visible after submission
    """
    page.get_by_role("link", name="Discrimination").click()
    page.get_by_label("Work - including colleagues,").check()
    page.get_by_role("button", name="Continue").click()

    # Check all selected options
    for selection in selections:
        page.get_by_label(selection).check()

    # Submit form
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_text(expected_heading)).to_be_visible()


class TestUnder18Form:
    # Page headings used in tests
    ARE_YOU_UNDER_18_HEADING = "Are you under 18?"
    CONTACT_PAGE_HEADING = "Contact Civil Legal Advice"
    LEGALAID_PAGE_HEADING = "Legal aid is available for this type of problem"

    def navigate_to_form(self, page: Page):
        page.get_by_role("link", name="Discrimination").click()
        page.get_by_label("Work - including colleagues").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Race, colour, ethnicity, nationality").check()
        page.get_by_role("button", name="Continue").click()

        expect(page.get_by_text(self.ARE_YOU_UNDER_18_HEADING)).to_be_visible()

    @pytest.mark.usefixtures("live_server")
    def test_are_you_under_18_form_yes(self, page: Page):
        self.navigate_to_form(page)
        page.get_by_label("Yes").check()
        page.get_by_role("button", name="Continue").click()
        expect(page.get_by_role("heading", name=self.CONTACT_PAGE_HEADING)).to_be_visible()

    @pytest.mark.usefixtures("live_server")
    def test_are_you_under_18_form_no(self, page: Page):
        self.navigate_to_form(page)
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        expect(page.get_by_text(self.LEGALAID_PAGE_HEADING)).to_be_visible()


class TestWhereMultipleSelections:
    @staticmethod
    def navigate_to_form(page: Page):
        page.get_by_role("link", name="Discrimination").click()
        page.get_by_label("Work - including colleagues").check()
        page.get_by_role("button", name="Continue").click()

    @pytest.mark.usefixtures("live_server")
    def test_select_exclusive_value(self, page: Page):
        self.navigate_to_form(page)
        page.get_by_role("checkbox", name="Disability, health condition").check()
        expect(page.get_by_role("checkbox", name="Disability, health condition")).to_be_checked()
        page.get_by_role("checkbox", name="None of these").check()
        expect(page.get_by_role("checkbox", name="Disability, health condition")).not_to_be_checked()

    @pytest.mark.usefixtures("live_server")
    def test_select_non_exclusive_values(self, page: Page):
        self.navigate_to_form(page)
        page.get_by_role("checkbox", name="Disability, health condition").check()
        page.get_by_role("checkbox", name="Age").check()
        expect(page.get_by_role("checkbox", name="Disability, health condition")).to_be_checked()
        expect(page.get_by_role("checkbox", name="Age")).to_be_checked()
