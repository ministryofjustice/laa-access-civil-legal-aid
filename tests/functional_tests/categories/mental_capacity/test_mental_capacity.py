from playwright.sync_api import Page, expect
import pytest
import re

in_scope_page_heading = "Legal aid is available for this type of problem"
find_a_legal_adviser_heading = "Find a legal adviser"
social_care_heading = "Care needs for disability and old age (social care)"

ROUTING = [
    {
        "link_text": "If someone cannot decide for themselves",
        "next_page_heading": find_a_legal_adviser_heading,
        "fala_categories": {"primary": "mhe", "secondary": "com"},
    },
    {
        "link_text": "Court of Protection",
        "next_page_heading": find_a_legal_adviser_heading,
        "fala_categories": {"primary": "mhe", "secondary": "com"},
    },
    {
        "link_text": "Mental health detention and tribunals",
        "next_page_heading": find_a_legal_adviser_heading,
        "fala_categories": {"primary": "mhe"},
    },
    {
        "link_text": "Care needs for disability and old age (social care)",
        "next_page_heading": social_care_heading,
    },
    {
        "link_text": "Next steps to get help",
        "next_page_heading": "Legal aid doesn’t cover all types of problem",
    },
]


@pytest.mark.usefixtures("live_server")
class TestMentalCapacityLandingPage:
    @pytest.mark.parametrize("routing", ROUTING)
    def test_onward_routing(self, page: Page, routing: dict):
        page.get_by_role("link", name="Mental capacity, mental health").click()
        page.get_by_role("link", name=routing["link_text"]).click()
        expect(page.get_by_text(routing["next_page_heading"])).to_be_visible()
        if "fala_categories" in routing:
            if "primary" in routing["fala_categories"]:
                primary_category = routing["fala_categories"]["primary"]
                expect(page).to_have_url(re.compile(f".*category={primary_category}*"))
            if "secondary" in routing["fala_categories"]:
                secondary_category = routing["fala_categories"]["secondary"]
                expect(page).to_have_url(
                    re.compile(f".*secondary_category={secondary_category}*")
                )
