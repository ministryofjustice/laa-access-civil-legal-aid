import pytest
from playwright.sync_api import Page, expect, Route, Request
from flask import url_for


def assert_page_has_errors(page: Page, errors_list: dict[str, str]) -> None:
    for field_name, error in errors_list.items():
        elements = page.locator(f".govuk-error-summary__list li a[href='#{field_name}']", has_text=error)
        for index in range(elements.count()):
            assert elements.nth(index).text_content().strip() == error, (
                f"Found element <em>{error}</em> but does not have error: {index}"
            )
        assert elements.count() > 0, f"Could not find error: <em>{error}</em> on the page"


@pytest.mark.usefixtures("live_server")
def test_booking_page__empty_form(page: Page) -> None:
    page.goto(url_for("contact_us.booking", _external=True))
    expect(page).to_have_title("Book an appointment with Civil Legal Advice - GOV.UK")
    page.get_by_role("button", name="Continue").click()
    assert_page_has_errors(page, {"full_name": "Enter your name"})


@pytest.mark.usefixtures("live_server")
def test_postcode_field(page: Page):
    def mock_postcode_lookup(route: Route, request: Request):
        route.fulfill(
            status=200,
            content_type="application/json",
            body='[{"formatted_address":"Ministry of Justice\\n10 South Colonnade\\nLondon\\nE14 4PU"},{"formatted_address":"Health & Safety Executive\\n10 South Colonnade\\nLondon\\nE14 4PU"},{"formatted_address":"Nhs Resolution\\n10 South Colonnade\\nLondon\\nE14 4PU"},{"formatted_address":"The Valuation Office Agency\\n10 South Colonnade\\nLondon\\nE14 4PU"},{"formatted_address":"Uk Sport\\n10 South Colonnade\\nLondon\\nE14 4PU"}]',
        )

    page.goto(url_for("contact_us.booking", _external=True))
    page.route("**/addresses/**", mock_postcode_lookup)

    postcode_element = page.get_by_role("textbox", name="Postcode (optional)")
    postcode_element.scroll_into_view_if_needed()
    postcode_element.fill("E14 4PU")

    page.get_by_role("button", name="Find UK Address").click()
    address_selector = page.locator("#address_finder")
    address_selector.wait_for(state="visible")
    address_selector.select_option(index=1)

    street_address = page.get_by_role("textbox", name="Enter your home address (optional)")
    expect(street_address).to_have_value("Ministry of Justice\n10 South Colonnade\nLondon\nE14 4PU", timeout=5000)
