import pytest
from playwright.sync_api import Page, expect
from tests.functional_tests.means_test.common_steps import fail_means_test


def navigate_to_means_test_hlpas(page: Page):
    page.get_by_role("link", name="Housing, homelessness, losing").click()
    page.get_by_role("link", name="Homelessness").click()
    page.get_by_role("button", name="Check if you qualify").click()


def navigate_to_means_test_no_hlpas(page: Page):
    page.get_by_role("link", name="Discrimination").click()
    page.get_by_role("checkbox", name="Work - including colleagues,").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("checkbox", name="Race, colour, ethnicity,").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("radio", name="No").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("button", name="Check if you qualify").click()


@pytest.mark.usefixtures("live_server")
def test_hlpas_user_journey(page: Page):
    navigate_to_means_test_hlpas(page)
    fail_means_test(page)
    expect(
        page.get_by_role("heading", name="You might qualify for free legal advice")
    ).to_be_visible()
    expect(page.get_by_role("button", name="Continue")).to_have_attribute(
        "href", "https://find-legal-advice.justice.gov.uk/check?categories=hlpas"
    )


@pytest.mark.usefixtures("live_server")
def test_non_hlpas_user_journey(page: Page):
    navigate_to_means_test_no_hlpas(page)
    fail_means_test(page)
    expect(
        page.get_by_role("heading", name="Legal aid doesn’t cover all types of problem")
    ).to_be_visible()
