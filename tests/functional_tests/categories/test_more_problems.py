import pytest
from playwright.sync_api import Page

FALA_ROUTES = [
    # Link text, FALA Primary Category, FALA Secondary Category
    ("Adopting a child from outside the UK", "mat", ""),
    (
        "Appeal a decision that you cannot work with children or vulnerable adults",
        "",
        "",
    ),
    ("Clinical negligence in babies", "med", ""),
    ("Compensation for abuse, assault or neglect", "aap", ""),
    ("Environmental pollution", "pub", ""),
    ("Inquests for family members", "", ""),
    ("Mental health detention", "mhe", ""),
    ("Proceeds of Crime Act", "crm", ""),
    ("Terrorism", "immas", "pub"),
    ("Trafficking, modern slavery", "immas", ""),
]


@pytest.mark.usefixtures("live_server")
class TestMoreProblems:
    @pytest.mark.parametrize("route, primary_category, secondary_category", FALA_ROUTES)
    def test_fala_routes(
        self, page: Page, route: str, primary_category: str, secondary_category: str
    ):
        page.get_by_role("link", name="More problems covered by legal aid").click()
        page.get_by_role("link", name=route).click()
        page.get_by_role("heading", name="Find a legal adviser").is_visible()
        if primary_category:
            assert f"category={primary_category}" in page.url
        if secondary_category:
            assert f"secondary_category={secondary_category}" in page.url
