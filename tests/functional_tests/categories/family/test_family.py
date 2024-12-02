from playwright.sync_api import Page, expect
import pytest

contact_us_page_heading = "Contact us page"
in_scope_page_heading = "Legal aid is available for this type of problem"

ROUTING = [
    {
        "link_text": "Children and social services, children in care",
        "next_page_heading": contact_us_page_heading,
    },
    {
        "link_text": "Problems with an ex-partner, divorce",
        "next_page_heading": contact_us_page_heading,
    },
    {
        "link_text": "If there is domestic abuse",
        "next_page_heading": contact_us_page_heading,
    },
    {"link_text": "Family mediation", "next_page_heading": in_scope_page_heading},
    {
        "link_text": "Child taken without your consent",
        "next_page_heading": contact_us_page_heading,
    },
    {
        "link_text": "Children with special educational needs and disabilities",
        "next_page_heading": in_scope_page_heading,
    },
    {
        "link_text": "Schools, colleges, other education settings",
        "next_page_heading": in_scope_page_heading,
    },
    {
        "link_text": "Forced marriage",
        "next_page_heading": in_scope_page_heading,
    },
    {"link_text": "Next steps to get help", "next_page_heading": "Referral page"},
]


@pytest.mark.usefixtures("live_server")
class TestFamilyLandingPage:
    @pytest.mark.parametrize("routing", ROUTING)
    def test_onward_routing(self, page: Page, routing: dict):
        page.get_by_role("link", name="Children, families and relationships").click()
        page.get_by_role("link", name=routing["link_text"]).click()
        expect(page.get_by_text(routing["next_page_heading"])).to_be_visible()
