import pytest
from playwright.sync_api import Page, expect
from flask import url_for


@pytest.fixture
def navigate_to_search(page: Page, live_server) -> None:
    """Common setup to navigate to the search page"""
    page.goto(url_for("find-a-legal-advisor.search", _external=True))


@pytest.mark.usefixtures("live_server")
class TestPostcodeSearch:
    def test_valid_uk_postcodes(self, page: Page, navigate_to_search) -> None:
        """Test various valid UK postcodes return results"""
        valid_postcodes = ["SW1A", "CF10", "EH1", "BT1"]

        for postcode in valid_postcodes:
            page.get_by_label("Postcode").click()
            page.get_by_label("Postcode").fill(postcode)
            page.get_by_role("button", name="Search").click()
            expect(
                page.get_by_role("heading", name="Contact a legal adviser")
            ).to_be_visible()
            page.get_by_role("link", name="Back").click()

    def test_channel_islands_postcodes(self, page: Page, navigate_to_search) -> None:
        """Test Channel Islands postcodes show no results"""
        channel_postcodes = ["JE2", "GY1"]

        for postcode in channel_postcodes:
            page.get_by_label("Postcode").click()
            page.get_by_label("Postcode").fill(postcode)
            page.get_by_role("button", name="Search").click()
            expect(
                page.get_by_role("link", name="No results returned for")
            ).to_be_visible()

    def test_isle_of_man_postcode(self, page: Page, navigate_to_search) -> None:
        """Test Isle of Man postcode shows no results"""
        page.get_by_label("Postcode").click()
        page.get_by_label("Postcode").fill("im1")
        page.get_by_role("button", name="Search").click()
        expect(
            page.get_by_role("link", name="No results returned for the")
        ).to_be_visible()

    def test_invalid_postcode_format(self, page: Page, navigate_to_search) -> None:
        """Test invalid postcode format shows error"""
        page.get_by_label("Postcode").click()
        page.get_by_label("Postcode").fill("Not a postcode")
        page.get_by_role("button", name="Search").click()
        expect(page.get_by_role("link", name="Postcode not found")).to_be_visible()

    def test_empty_postcode(self, page: Page, navigate_to_search) -> None:
        """Test empty postcode shows error"""
        page.get_by_label("Postcode").click()
        page.get_by_label("Postcode").fill("    ")
        page.get_by_role("button", name="Search").click()
        expect(page.get_by_role("link", name="Postcode not found")).to_be_visible()

    def test_postcode_with_leading_spaces(self, page: Page, navigate_to_search) -> None:
        """Test postcode with leading spaces works"""
        page.get_by_label("Postcode").click()
        page.get_by_label("Postcode").fill("    sw1")
        page.get_by_role("button", name="Search").click()
        expect(
            page.get_by_role("heading", name="Contact a legal adviser")
        ).to_be_visible()
