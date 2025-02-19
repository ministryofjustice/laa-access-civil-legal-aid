import pytest
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
def test_time_fast_forward(page: Page):
    expect(page.get_by_label("Your application will time out soon")).to_be_hidden()

    # Fast-forward 26 minutes
    page.evaluate("""() => {
        const originalNow = Date.now;
        Date.now = () => originalNow() + 26 * 60 * 1000;
    }""")

    expect(page.get_by_label("Your application will time out soon")).to_be_visible()
