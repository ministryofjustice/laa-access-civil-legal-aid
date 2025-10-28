import pytest
from playwright.sync_api import Page, expect
from tests.functional_tests.means_test.common_steps import fail_means_test


def navigate_to_means_test_discrimination(page: Page):
    page.get_by_role("link", name="Discrimination").click()
    page.get_by_role("checkbox", name="Work - including colleagues,").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("checkbox", name="Race, colour, ethnicity,").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("radio", name="No").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("button", name="Check if you qualify").click()


def navigate_to_means_test_education(page: Page):
    page.get_by_role("link", name="Special educational needs and").click()
    page.get_by_role("link", name="Help with a child or young").click()
    page.get_by_role("radio", name="No").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("button", name="Check if you qualify").click()


def navigate_to_means_test_family(page: Page):
    page.get_by_role("link", name="Children, families,").click()
    page.get_by_role("link", name="Family mediation").click()
    page.get_by_role("radio", name="Yes").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("button", name="Check if you qualify").click()


@pytest.mark.usefixtures("live_server")
def test_discrimination_user_journey(page: Page):
    navigate_to_means_test_discrimination(page)
    fail_means_test(page)
    expect(page.get_by_role("heading", name="You’re unlikely to get legal aid")).to_be_visible()
    expect(page.get_by_role("heading", name="Help organisations for problems about discrimination")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_education_user_journey(page: Page):
    navigate_to_means_test_education(page)
    fail_means_test(page)
    expect(page.get_by_role("heading", name="You’re unlikely to get legal aid")).to_be_visible()
    expect(
        page.get_by_role(
            "heading", name="Help organisations for problems about special educational needs and disability (SEND)"
        )
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_family_user_journey(page: Page):
    navigate_to_means_test_family(page)
    fail_means_test(page)
    expect(page.get_by_role("heading", name="You’re unlikely to get legal aid")).to_be_visible()
    expect(
        page.get_by_role("heading", name="Help organisations for problems about children, families, relationships")
    ).to_be_visible()
