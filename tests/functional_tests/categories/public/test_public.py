from playwright.sync_api import Page, expect
import pytest


@pytest.mark.usefixtures("live_server")
class TestPublicLandingPage:
    def assert_outcome(self, page: Page, option: str) -> None:
        page.get_by_label(option).check()
        page.get_by_role("button", name="Continue").click()
        expect(page.get_by_text("Find a legal adviser")).to_be_visible()
        expect(page.get_by_text("For welfare benefits")).to_be_visible()

    def test_public_yes(self, page: Page):
        page.get_by_role(
            "link", name="Legal action against police and public organisations"
        ).click()
        expect(
            page.get_by_role(
                "heading", name="Legal action against police and public organisations"
            )
        ).to_be_visible()
        page.get_by_role("button", name="Continue").click()
        expect(
            page.get_by_text("Is this to do with police, prisons or detention centres?")
        ).to_be_visible()
        page.get_by_label("Yes").check()
        page.get_by_role("button", name="Continue").click()
        expect(page.get_by_text("Find a legal adviser"))
        expect(page.get_by_text("For claims against public authorities"))

    def test_public_no(self, page: Page):
        page.get_by_role(
            "link", name="Legal action against police and public organisations"
        ).click()
        expect(
            page.get_by_role(
                "heading", name="Legal action against police and public organisations"
            )
        ).to_be_visible()
        page.get_by_role("button", name="Continue").click()
        expect(
            page.get_by_text("Is this to do with police, prisons or detention centres?")
        ).to_be_visible()
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        expect(page.get_by_text("Find a legal adviser"))
        expect(page.get_by_text("For public law"))

    def test_public_cannot_find_your_problem(self, page: Page):
        page.get_by_role(
            "link", name="Legal action against police and public organisations"
        ).click()
        page.get_by_role("link", name="Next steps to get help").click()
        expect(
            page.get_by_role(
                "heading", name="Sorry, you’re not likely to get legal aid"
            )
        ).to_be_visible()
