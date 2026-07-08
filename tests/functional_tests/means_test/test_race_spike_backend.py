"""LGA-3883 spike.

Real CI failures (not the port-binding theory we ruled out) include a means
test session landing on the wrong page with another session's content
(test_review_page_success_access_completed_means). test.yml runs a single
shared cla_backend container for the whole functional_test job, hit
concurrently by every xdist worker. If that shared backend ever
cross-assigns/overwrites an eligibility_check record between two concurrent
sessions, one browser's review page would show another browser's answers.

Each parametrized case here injects a distinct numeric fingerprint into the
means test's "Maintenance received" answer and asserts the review page shows
only that fingerprint. A failure (wrong or missing fingerprint) means two
concurrent sessions collided on the shared backend.

Remove this file once LGA-3883 is confirmed/fixed.
"""

import pytest
from flask import url_for
from playwright.sync_api import Page, expect

FINGERPRINTS = [f"{100 + n}.01" for n in range(24)]


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("fingerprint", FINGERPRINTS)
def test_no_cross_contamination_between_concurrent_means_tests(page: Page, fingerprint):
    page.goto(url_for("categories.index", _external=True))
    page.get_by_role("link", name="Housing, homelessness, losing your home").click()
    page.get_by_role("link", name="Homelessness").click()
    page.get_by_role("button", name="Check if you qualify financially").click()

    page.locator("#has_partner-2").check()
    page.get_by_role("group", name="Do you receive any benefits (").get_by_label("No").check()
    page.get_by_role("group", name="Do you have any children aged").get_by_label("No").check()
    page.get_by_role("group", name="Do you have any dependants").get_by_label("No").check()
    page.get_by_role("group", name="Do you own any property?").get_by_label("No").check()
    page.get_by_role("group", name="Are you employed?").get_by_label("No").check()
    page.get_by_role("group", name="Are you self-employed?").get_by_label("No").check()
    page.get_by_role("group", name="Are you or your partner (if").get_by_label("No").check()
    page.get_by_role("group", name="Do you have any savings or").get_by_label("No").check()
    page.get_by_role("group", name="Do you have any valuable").get_by_label("No").check()
    page.get_by_role("button", name="Continue").click()

    # Fingerprint value: unique per parametrized case, used to detect if this
    # session's review page ends up showing a different concurrent session's data.
    page.get_by_role("group", name="Maintenance received").get_by_label("Amount").click()
    page.get_by_role("group", name="Maintenance received").get_by_label("Amount").fill(fingerprint)
    page.get_by_role("group", name="Maintenance received").get_by_label("Frequency").select_option("per_week")
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_role("heading", name="Check your answers and confirm")).to_be_visible()

    income_section = page.locator(".govuk-summary-list[data-question='Your income and tax']")
    expect(income_section).to_contain_text(fingerprint)

    other_fingerprints = [fp for fp in FINGERPRINTS if fp != fingerprint]
    for other in other_fingerprints:
        expect(income_section).not_to_contain_text(other)
