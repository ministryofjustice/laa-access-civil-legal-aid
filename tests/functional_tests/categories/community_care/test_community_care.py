from playwright.sync_api import Page, expect
import pytest

fala_page_heading = ["Find a legal adviser", "community care"]

ROUTING = [
    {
        "link_text": "Care from the council (local authority)",
        "next_page_heading": fala_page_heading,
    },
    {
        "link_text": "If you’re a carer",
        "next_page_heading": fala_page_heading,
    },
    {
        "link_text": "If you receive care in your own home",
        "next_page_heading": fala_page_heading,
    },
    {
        "link_text": "If care or funding stops",
        "next_page_heading": fala_page_heading,
    },
    {
        "link_text": "Placements, care homes and care housing",
        "next_page_heading": fala_page_heading,
    },
    {
        "link_text": "Problems with the quality of care, safeguarding",
        "next_page_heading": fala_page_heading,
    },
    {
        "link_text": "If you’re a care leaver",
        "next_page_heading": fala_page_heading,
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
        page.get_by_role("link", name="Care needs for disability and old age (social care)").click()
        page.get_by_role("link", name=routing["link_text"]).click()

        next_page_heading = routing["next_page_heading"]
        next_page_heading = next_page_heading if isinstance(next_page_heading, list) else [next_page_heading]
        for page_heading in next_page_heading:
            expect(page.get_by_text(page_heading)).to_be_visible()
