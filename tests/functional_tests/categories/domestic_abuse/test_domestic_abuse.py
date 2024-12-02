from playwright.sync_api import Page, expect
import pytest

risk_of_harm_page_heading = "Are you or your children at immediate risk of harm?"
in_scope_page_heading = "Legal aid is available for this type of problem"
contact_us_page_heading = "Contact us page"
housing_page_heading = "Housing, homelessness, losing your home"

ROUTING = [
    {
        "link_text": "Help to protect you and your children",
        "next_page_heading": risk_of_harm_page_heading,
    },
    {
        "link_text": "Leaving an abusive relationship",
        "next_page_heading": risk_of_harm_page_heading,
    },
    {
        "link_text": "Problems with an ex-partner: children or money",
        "next_page_heading": risk_of_harm_page_heading,
    },
    {
        "link_text": "Problems with neighbours, landlords or other people",
        "next_page_heading": contact_us_page_heading,
    },
    {
        "link_text": "Housing, homelessness, losing your home",
        "next_page_heading": housing_page_heading,
    },
    {
        "link_text": "Forced marriage",
        "next_page_heading": risk_of_harm_page_heading,
    },
    {
        "link_text": "Female genital mutilation (FGM)",
        "next_page_heading": risk_of_harm_page_heading,
    },
    {"link_text": "Next steps to get help", "next_page_heading": "Referral page"},
]


@pytest.mark.usefixtures("live_server")
class TestFamilyLandingPage:
    @pytest.mark.parametrize("routing", ROUTING)
    def test_onward_routing(self, page: Page, routing: dict):
        page.get_by_role("link", name="Domestic abuse").click()
        expect(
            page.get_by_role("button", name="Emergency Exit this page")
        ).to_be_visible()
        page.get_by_role("link", name=routing["link_text"]).click()
        expect(page.get_by_text(routing["next_page_heading"])).to_be_visible()
        if page.get_by_text(routing["next_page_heading"]) == risk_of_harm_page_heading:
            expect(
                page.get_by_role("button", name="Emergency Exit this page")
            ).to_be_visible()
            page.get_by_label("Yes").click()
            page.get_by_role("button", name="submit").click()
            expect(page.get_by_text(in_scope_page_heading)).to_be_visible()
