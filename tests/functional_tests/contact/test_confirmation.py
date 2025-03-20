import pytest
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
def test_confirmation_page_email(page: Page):
    page.get_by_role("link", name="Contact us").click()

    page.get_by_role("button", name="Continue to contact CLA").click()

    expect(
        page.get_by_role("heading", name="Contact Civil Legal Advice")
    ).to_be_visible()

    page.get_by_role("textbox", name="Your full name").fill("Test")

    page.get_by_role("radio", name="I will call you").check()

    page.get_by_role("button", name="Submit details").click()

    expect(
        page.get_by_role("heading", name="Your details have been submitted")
    ).to_be_visible()

    # This email address is provided by GOV.UK Notify for testing purposes
    page.get_by_role("textbox", name="Receive this confirmation by").fill(
        "simulate-delivered@notifications.service.gov.uk"
    )

    page.get_by_role("button", name="Send").click()

    expect(
        page.get_by_text(
            "Your reference number was sent to simulate-delivered@notifications.service.gov.uk."
        )
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_family_category(page: Page):
    page.get_by_role("link", name="Children, families,").click()
    page.get_by_role("link", name="Children and social services").click()
    page.get_by_role("textbox", name="Your full name").fill("John Doe")
    page.get_by_role("radio", name="I will call you").check()
    page.get_by_role("button", name="Submit details").click()
    expect(
        page.get_by_text(
            "If your case involves domestic abuse or violence, the specialist adviser will need evidence of this"
        )
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_domestic_abuse_category(page: Page):
    page.get_by_role("link", name="Domestic abuse").click()
    page.get_by_role("link", name="Help to keep yourself safe").click()
    page.get_by_role("radio", name="Yes").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("textbox", name="Your full name").fill("John Doe")
    page.get_by_role("radio", name="I will call you").check()
    page.get_by_role("button", name="Submit details").click()
    expect(
        page.get_by_text(
            "Please be aware that the specialist adviser will need evidence of the domestic violence"
        )
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_housing_category(page: Page):
    page.get_by_role("link", name="Housing, homelessness, losing").click()
    page.get_by_role("link", name="Homelessness").click()
    page.get_by_role("paragraph").filter(
        has_text="Fill in the ' contact CLA '"
    ).get_by_role("link").click()
    page.get_by_role("textbox", name="Your full name").fill("John Doe")
    page.get_by_role("radio", name="I will call you").check()
    page.get_by_role("button", name="Submit details").click()
    expect(
        page.get_by_text(
            "Warning If you have a court hearing date it is important that you get advice as soon as possible."
        )
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_thirdparty_callback(page: Page):
    page.get_by_role("link", name="Contact us").click()
    page.get_by_role("button", name="Continue to contact CLA").click()
    page.get_by_role("textbox", name="Your full name").fill("John Doe")
    page.get_by_role("radio", name="Call someone else instead of").check()
    page.get_by_role("textbox", name="Full name of the person to").fill("Jane Doe")
    page.get_by_label("Relationship to you").select_option("family_friend")
    page.get_by_role("textbox", name="Phone number").fill("12345")
    page.get_by_role("radio", name="Call on another day").check()
    page.locator("#thirdparty_call_another_day").select_option(index=1)
    page.locator("#thirdparty_call_another_time").select_option(index=1)
    page.get_by_role("button", name="Submit details").click()
    expect(
        page.get_by_text(
            "Your details have been submitted and an operator will call the person you nominated at least once during your chosen time, or as close to the time as possible"
        )
    ).to_be_visible()
    expect(
        page.get_by_text("The first person they speak to will be an operator")
    ).to_be_visible()
    expect(
        page.get_by_text(
            "If it looks like you might qualify for legal aid they’ll be put through to a specialist adviser, who will make the final decision on your case."
        )
    ).to_be_visible()
