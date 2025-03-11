from playwright.sync_api import Page, expect


def fail_means_test(page: Page):
    """Needs to start from the beginning of the means test"""
    page.locator("#has_partner-2").check()
    page.get_by_role("group", name="Do you receive any benefits (").get_by_label(
        "No"
    ).check()
    page.get_by_role("group", name="Do you have any children aged").get_by_label(
        "No"
    ).check()
    page.get_by_role("group", name="Do you have any dependants").get_by_label(
        "No"
    ).check()
    page.get_by_role("group", name="Do you own any property?").get_by_label(
        "No"
    ).check()
    page.get_by_role("group", name="Are you employed?").get_by_label("No").check()
    page.get_by_role("group", name="Are you self-employed?").get_by_label("No").check()
    page.get_by_role("group", name="Are you or your partner (if").get_by_label(
        "No"
    ).check()
    page.get_by_role("group", name="Do you have any savings or").get_by_label(
        "No"
    ).check()
    page.get_by_role("group", name="Do you have any valuable").get_by_label(
        "No"
    ).check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("group", name="Maintenance received").get_by_label(
        "Amount"
    ).click()
    page.get_by_role("group", name="Maintenance received").get_by_label("Amount").fill(
        "9999999"
    )
    page.get_by_role("group", name="Maintenance received").get_by_label(
        "Frequency"
    ).select_option("per_week")
    page.get_by_role("group", name="Pension received").get_by_label("Amount").click()
    page.get_by_role("group", name="Pension received").get_by_label("Amount").fill(
        "999999"
    )
    page.get_by_role("group", name="Pension received").get_by_label(
        "Frequency"
    ).select_option("per_week")
    page.get_by_role("group", name="Any other income").get_by_label("Amount").click()
    page.get_by_role("group", name="Any other income").get_by_label("Amount").fill(
        "999999"
    )
    page.get_by_role("group", name="Any other income").get_by_label(
        "Frequency"
    ).select_option("per_week")
    page.get_by_role("button", name="Continue").click()
    expect(
        page.get_by_role("heading", name="Check your answers and confirm")
    ).to_be_visible()
    page.get_by_role("button", name="Continue").click()
