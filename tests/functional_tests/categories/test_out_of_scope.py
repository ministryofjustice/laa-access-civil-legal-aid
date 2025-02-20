import pytest
from playwright.sync_api import Page, expect

CANNOT_FIND_PROBLEM_HEADING = "Sorry, you’re not likely to get legal aid"
NEXT_STEPS_HEADING = "Next steps to get help"


@pytest.mark.usefixtures("live_server")
def test_more_problems(page: Page):
    page.get_by_role("link", name="More problems covered by legal aid").click()
    page.get_by_role("link", name="Next steps to get help").click()
    expect(
        page.get_by_role("heading", name=CANNOT_FIND_PROBLEM_HEADING)
    ).to_be_visible()
    page.get_by_role("button", name="Next steps to get help").click()
    expect(page.get_by_role("heading", name=NEXT_STEPS_HEADING)).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_community_care(page: Page):
    page.get_by_role(
        "link", name="Care needs for disability and old age (social care)"
    ).click()
    page.get_by_role("link", name="Next steps to get help").click()
    expect(
        page.get_by_role("heading", name=CANNOT_FIND_PROBLEM_HEADING)
    ).to_be_visible()
    page.get_by_role("button", name="Next steps to get help").click()
    expect(page.get_by_role("heading", name=NEXT_STEPS_HEADING)).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_public_law(page: Page):
    page.get_by_role(
        "link", name="Legal action against police and public organisations"
    ).click()
    page.get_by_role("link", name="Next steps to get help").click()
    expect(
        page.get_by_role("heading", name=CANNOT_FIND_PROBLEM_HEADING)
    ).to_be_visible()
    page.get_by_role("button", name="Next steps to get help").click()
    expect(page.get_by_role("heading", name=NEXT_STEPS_HEADING)).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_mental_capacity(page: Page):
    page.get_by_role("link", name="Mental capacity, mental health").click()
    page.get_by_role("link", name="Next steps to get help").click()
    expect(
        page.get_by_role("heading", name=CANNOT_FIND_PROBLEM_HEADING)
    ).to_be_visible()
    page.get_by_role("button", name="Next steps to get help").click()
    expect(page.get_by_role("heading", name=NEXT_STEPS_HEADING)).to_be_visible()


onward_links = [
    (
        "free or affordable legal help",
        "Finding free or affordable legal help - Citizens Advice",
    ),
    ("Citizen’s Advice", "Contact us - Citizens Advice"),
    ("Advicelocal", "Find an adviser | Advicelocal"),
    ("exceptional case funding", "Legal aid: Funding for exceptional cases - GOV.UK"),
    (
        "What did you think of this service?",
        "Give feedback on Check if you can get legal aid - GOV.UK",
    ),
]


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("onward_link_text, expected_title", onward_links)
def test_onward_links(page: Page, onward_link_text, expected_title):
    page.get_by_role("link", name="Mental capacity, mental health").click()
    page.get_by_role("link", name="Next steps to get help").click()
    page.get_by_role("button", name="Next steps to get help").click()
    with page.expect_popup() as popup_info:
        page.get_by_role("link", name=onward_link_text).click()
    popup = popup_info.value

    expect(popup).to_have_title(expected_title)
