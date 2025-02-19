import pytest
from playwright.sync_api import Page, expect

CANNOT_FIND_PROBLEM_HEADING = "Sorry, you’re not likely to get legal aid"


@pytest.mark.usefixtures("live_server")
def test_more_problems(page: Page):
    page.get_by_role("link", name="More problems covered by legal aid").click()
    page.get_by_role("link", name="Next steps to get help").click()
    expect(
        page.get_by_role("heading", name=CANNOT_FIND_PROBLEM_HEADING)
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_community_care(page: Page):
    page.get_by_role(
        "link", name="Care needs for disability and old age (social care)"
    ).click()
    page.get_by_role("link", name="Next steps to get help").click()
    expect(
        page.get_by_role("heading", name=CANNOT_FIND_PROBLEM_HEADING)
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_public_law(page: Page):
    page.get_by_role(
        "link", name="Legal action against police and public organisations"
    ).click()
    page.get_by_role("link", name="Next steps to get help").click()
    expect(
        page.get_by_role("heading", name=CANNOT_FIND_PROBLEM_HEADING)
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_mental_capacity(page: Page):
    page.get_by_role("link", name="Mental capacity, mental health").click()
    page.get_by_role("link", name="Next steps to get help").click()
    expect(
        page.get_by_role("heading", name=CANNOT_FIND_PROBLEM_HEADING)
    ).to_be_visible()
