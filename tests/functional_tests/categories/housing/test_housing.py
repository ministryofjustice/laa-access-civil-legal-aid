from playwright.sync_api import Page, expect
import pytest

in_scope_page_heading = "Legal aid is available for this type of problem"

ROUTING = [
    {"link_text": "Homelessness", "next_page_heading": in_scope_page_heading},
    {"link_text": "Eviction", "next_page_heading": in_scope_page_heading},
    {
        "link_text": "Forced to sell or losing the home you own",
        "next_page_heading": in_scope_page_heading,
    },
    {"link_text": "Repairs", "next_page_heading": in_scope_page_heading},
    {
        "link_text": "Problems with council housing",
        "next_page_heading": in_scope_page_heading,
    },
    {
        "link_text": "Being threatened or harassed where you live",
        "next_page_heading": in_scope_page_heading,
    },
    {
        "link_text": "If you’re an asylum-seeker",
        "next_page_heading": in_scope_page_heading,
    },
    {
        "link_text": "Discrimination",
        "next_page_heading": "Where did the discrimination happen?",
    },
    {
        "link_text": "If you’ve been accused of anti-social behaviour",
        "next_page_heading": in_scope_page_heading,
    },
    {
        "link_text": "Next steps to get help",
        "next_page_heading": "Sorry, you’re not likely to get legal aid",
    },
]


@pytest.mark.usefixtures("live_server")
class TestHousingLandingPage:
    @pytest.mark.parametrize("routing", ROUTING)
    def test_onward_routing(self, page: Page, routing: dict):
        page.get_by_role("link", name="Housing, homelessness, losing your home").click()
        page.get_by_role("link", name=routing["link_text"]).click()
        expect(page.get_by_text(routing["next_page_heading"])).to_be_visible()
