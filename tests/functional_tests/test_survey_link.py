import pytest
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
class TestSurveyLinks:
    def test_next_steps(self, page: Page):
        page.get_by_role("link", name="More problems covered by").click()
        page.get_by_role("link", name="Next steps to get help").click()
        page.get_by_role("button", name="Next steps to get help").click()
        expect(page.get_by_role("link", name="Tell us what you think of this service")).to_have_attribute(
            "href", value="https://www.smartsurvey.co.uk/s/legalaid1/"
        )

    def test_next_steps_alternative_help(self, page: Page):
        page.get_by_role("link", name="Housing, homelessness, losing").click()
        page.get_by_role("link", name="Next steps to get help").click()
        page.get_by_role("button", name="Next steps to get help").click()
        expect(page.get_by_role("link", name="Tell us what you think of this service")).to_have_attribute(
            "href", value="https://www.smartsurvey.co.uk/s/legalaid3/"
        )

    def test_confirmation_page(self, page: Page):
        page.get_by_role("link", name="Contact us").click()
        page.get_by_role("button", name="Continue to contact CLA").click()
        page.get_by_role("textbox", name="Your full name").fill("John Doe")
        page.get_by_role("radio", name="I will call you").check()
        page.get_by_role("button", name="Submit details").click()
        expect(page.get_by_role("link", name="Tell us what you think of this service")).to_have_attribute(
            "href", value="https://www.smartsurvey.co.uk/s/legalaid2/"
        )
