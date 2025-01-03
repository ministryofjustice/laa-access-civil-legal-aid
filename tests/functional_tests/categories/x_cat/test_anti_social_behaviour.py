from playwright.sync_api import Page, expect
import pytest

in_scope_page_heading = "Legal aid is available for this type of problem"
fala_page_heading = "Find a legal adviser"

ROUTING = [
    {"answer": "Yes", "next_page_heading": in_scope_page_heading},
    {"answer": "No", "next_page_heading": fala_page_heading},
]


@pytest.mark.usefixtures("live_server")
class TestAntiSocialBehaviourForm:
    @pytest.mark.parametrize("routing", ROUTING)
    def test_onward_routing(self, page: Page, routing: dict):
        page.get_by_role("link", name="More problems covered by").click()
        page.get_by_role("link", name="Anti-social behaviour and").click()
        page.get_by_label(routing["answer"]).check()
        page.get_by_role("button", name="Continue").click()
        expect(page.get_by_text(routing["next_page_heading"])).to_be_visible()
