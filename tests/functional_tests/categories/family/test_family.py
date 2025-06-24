from playwright.sync_api import Page, expect
import pytest

contact_us_page_heading = "Contact Civil Legal Advice"
in_scope_page_heading = "Legal aid is available for this type of problem"

ROUTING = [
    {
        "link_text": "Children and social services, children in care",
        "next_page_heading": contact_us_page_heading,
    },
    {
        "link_text": "Problems with an ex-partner, divorce",
        "next_page_heading": "Problems about children and money when a relationship ends",
    },
    {
        "link_text": "If there is domestic abuse",
        "next_page_heading": "Are you worried about someone's safety?",
    },
    {
        "link_text": "Family mediation",
        "next_page_heading": "Have you taken part in a family mediation session?",
    },
    {
        "link_text": "Child taken without your consent",
        "next_page_heading": contact_us_page_heading,
    },
    {
        "link_text": "Children with special educational needs and disabilities",
        "next_page_heading": "Special educational needs and disability (SEND)",
    },
    {
        "link_text": "Schools, colleges, other education settings",
        "next_page_heading": in_scope_page_heading,
    },
    {
        "link_text": "Forced marriage",
        "next_page_heading": "Are you worried about someone's safety?",
    },
    {
        "link_text": "Next steps to get help",
        "next_page_heading": "Sorry, you’re not likely to get legal aid",
    },
]


@pytest.mark.usefixtures("live_server")
class TestFamilyLandingPage:
    @pytest.mark.parametrize("routing", ROUTING)
    def test_onward_routing(self, page: Page, routing: dict):
        page.get_by_role("link", name="Children, families, relationships").click()
        page.get_by_role("link", name=routing["link_text"]).click()
        expect(page.get_by_role("heading", name=routing["next_page_heading"])).to_be_visible()
