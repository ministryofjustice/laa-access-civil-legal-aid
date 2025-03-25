from playwright.sync_api import Page, expect
import pytest


child_in_care_heading = "Is this about a child who is or has been in care?"
legalaid_available_page = "Legal aid is available for this type of problem"
contact_page_heading = "Contact Civil Legal Advice"
ROUTING = [
    {
        "link_text": "Help with a child or young person's SEND",
        "next_page_heading": child_in_care_heading,
    },
    {
        "link_text": "SEND tribunals",
        "next_page_heading": child_in_care_heading,
    },
    {
        "link_text": "Child treated unfairly at school, discrimination",
        "next_page_heading": legalaid_available_page,
    },
    {
        "link_text": "Other problems with schools",
        "next_page_heading": legalaid_available_page,
    },
    {
        "link_text": "Care needs for disability (social care)",
        "next_page_heading": "Care needs for disability and old age (social care)",
    },
    {
        "link_text": "Next steps to get help",
        "next_page_heading": "Sorry, you’re not likely to get legal aid",
    },
]


@pytest.mark.usefixtures("live_server")
class TestSendLandingPage:
    @pytest.mark.parametrize("routing", ROUTING)
    def test_onward_routing(self, page: Page, routing: dict):
        page.get_by_role("link", name="Special educational needs and disability (SEND)").click()
        page.get_by_role("link", name=routing["link_text"]).click()

        next_page_heading = routing["next_page_heading"]
        next_page_heading = next_page_heading if isinstance(next_page_heading, list) else [next_page_heading]
        for page_heading in next_page_heading:
            expect(page.get_by_role("heading", name=page_heading)).to_be_visible()

    def test_child_in_care_form_yes(self, page: Page):
        page.get_by_role("link", name="Special educational needs and disability (SEND)").click()
        page.get_by_role("link", name="SEND tribunals").click()
        page.get_by_label("Yes").check()
        page.get_by_role("button", name="Continue").click()
        expect(page.get_by_role("heading", name=contact_page_heading)).to_be_visible()

    def test_child_in_care_form_no(self, page: Page):
        page.get_by_role("link", name="Special educational needs and disability (SEND)").click()
        page.get_by_role("link", name="SEND tribunals").click()
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        expect(page.get_by_role("heading", name=legalaid_available_page)).to_be_visible()
