from playwright.sync_api import Page, expect
import pytest


@pytest.mark.usefixtures("live_server")
class TestAsylumAndImmigrationLandingPage:
    def assert_outcome(self, page: Page, option: str) -> None:
        page.get_by_label(option).check()
        page.get_by_role("button", name="Continue").click()
        expect(page.get_by_text("Find a legal adviser")).to_be_visible()
        expect(page.get_by_text("For welfare benefits")).to_be_visible()

    def test_appeal_upper_tribunal(self, page: Page):
        page.get_by_role("link", name="Benefits").click()
        self.assert_outcome(page, "Upper Tribunal (Administrative Appeals Chamber)")

    def test_appeal_supreme_court(self, page: Page):
        page.get_by_role("link", name="Benefits").click()
        self.assert_outcome(page, "Supreme Court")

    def test_appeal_appeal_court(self, page: Page):
        page.get_by_role("link", name="Benefits").click()
        self.assert_outcome(page, "Court of Appeal")

    def test_appeal_none(self, page: Page):
        page.get_by_role("link", name="Benefits").click()
        page.get_by_label("None of the above").check()
        page.get_by_role("button", name="Continue").click()
        expect(
            page.get_by_text("Legal aid doesn’t cover all types of problem")
        ).to_be_visible()
