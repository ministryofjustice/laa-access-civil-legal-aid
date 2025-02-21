from playwright.sync_api import Page, expect
import pytest

in_scope_page_heading = "Legal aid is available for this type of problem"
fala_page_heading = "Find a legal adviser"

ROUTING = [
    {"link_text": "Applying for asylum", "next_page_heading": fala_page_heading},
    {
        "link_text": "Housing and homelessness",
        "next_page_heading": in_scope_page_heading,
    },
    {
        "link_text": "Stay in the UK if you experienced domestic abuse",
        "next_page_heading": fala_page_heading,
    },
    {
        "link_text": "Help if you’re being detained",
        "next_page_heading": fala_page_heading,
    },
    {
        "link_text": "Trafficking, modern slavery",
        "next_page_heading": fala_page_heading,
    },
    {
        "link_text": "Next steps to get help",
        "next_page_heading": "Sorry, you’re not likely to get legal aid",
    },
]


@pytest.mark.usefixtures("live_server")
class TestAsylumAndImmigrationLandingPage:
    @pytest.mark.parametrize("routing", ROUTING)
    def test_onward_routing(self, page: Page, routing: dict):
        page.get_by_role("link", name="Asylum and immigration").click()
        page.get_by_role("link", name=routing["link_text"]).click()
        expect(page.get_by_text(routing["next_page_heading"])).to_be_visible()
