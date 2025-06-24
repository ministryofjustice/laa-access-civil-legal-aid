import pytest
from playwright.sync_api import Page, expect

CANNOT_FIND_PROBLEM_HEADING = "Sorry, you’re not likely to get legal aid"
NEXT_STEPS_HEADING = "Next steps to get help"


@pytest.mark.usefixtures("live_server")
def test_more_problems(page: Page):
    page.get_by_role("link", name="More problems covered by legal aid").click()
    page.get_by_role("link", name="Next steps to get help").click()
    expect(page.get_by_role("heading", name=CANNOT_FIND_PROBLEM_HEADING)).to_be_visible()
    page.get_by_role("button", name="Next steps to get help").click()
    expect(page.get_by_role("heading", name=NEXT_STEPS_HEADING)).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_community_care(page: Page):
    page.get_by_role("link", name="Care needs for disability and old age (social care)").click()
    page.get_by_role("link", name="Next steps to get help").click()
    expect(page.get_by_role("heading", name=CANNOT_FIND_PROBLEM_HEADING)).to_be_visible()
    page.get_by_role("button", name="Next steps to get help").click()
    expect(page.get_by_role("heading", name=NEXT_STEPS_HEADING)).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_public_law(page: Page):
    page.get_by_role("link", name="Legal action against police and public organisations").click()
    page.get_by_role("link", name="Next steps to get help").click()
    expect(page.get_by_role("heading", name=CANNOT_FIND_PROBLEM_HEADING)).to_be_visible()
    page.get_by_role("button", name="Next steps to get help").click()
    expect(page.get_by_role("heading", name=NEXT_STEPS_HEADING)).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_mental_capacity(page: Page):
    page.get_by_role("link", name="Mental capacity, mental health").click()
    page.get_by_role("link", name="Next steps to get help").click()
    expect(page.get_by_role("heading", name=CANNOT_FIND_PROBLEM_HEADING)).to_be_visible()
    page.get_by_role("button", name="Next steps to get help").click()
    expect(page.get_by_role("heading", name=NEXT_STEPS_HEADING)).to_be_visible()


onward_links = [
    "free or affordable legal help",
    "Citizen’s Advice (opens new tab)",
    "Advicelocal (opens new tab)",
    "exceptional case funding",
    "Tell us what you think of this service (opens new tab)",
]


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("onward_link_text", onward_links)
def test_onward_links_open_in_new_tab(page: Page, onward_link_text):
    page.get_by_role("link", name="More problems covered by legal aid").click()
    page.get_by_role("link", name="Next steps to get help").click()
    page.get_by_role("button", name="Next steps to get help").click()

    link = page.get_by_role("link", name=onward_link_text)

    # Check if the link has target="_blank" attribute (opens in new tab)
    target_attr = link.get_attribute("target")
    assert target_attr == "_blank", f"Link '{onward_link_text}' does not have target='_blank'"
