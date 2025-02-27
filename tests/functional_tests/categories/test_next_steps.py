import pytest
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize(
    "category_name, expected_text",
    [
        pytest.param(
            "Children, families, relationships",
            "These organisations give free, independent advice for problems about children, families and relationships.",
            id="family-category",
        ),
        pytest.param(
            "Police and public organisations",
            "These organisations give free, independent advice for problems with police and public organisations.",
            id="public-law-category",
        ),
        pytest.param(
            "Mental capacity, mental health",
            "These organisations give free, independent advice for problems about mental health and mental capacity.",
            id="mental-health-category",
        ),
        pytest.param(
            "Asylum and immigration",
            "These organisations give free, independent advice for problems about asylum and immigration.",
            id="asylum-immigration-category",
        ),
        pytest.param(
            "Care needs for disability and old age (social care)",
            "These organisations give free, independent advice for problems about disability and old age (social care).",
            id="community-care-category",
        ),
        pytest.param(
            "Housing, homelessness, losing your home",
            "These organisations give free, independent advice for problems about housing.",
            id="housing-category",
        ),
        pytest.param(
            "Special educational needs and disability (SEND)",
            "These organisations give free, independent advice for problems about special educational needs (SEND).",
            id="send-category",
        ),
    ],
)
def test_category_next_steps_page(page: Page, category_name: str, expected_text: str):
    page.get_by_role("link", name=category_name).click()
    page.get_by_role("link", name="Next steps to get help").click()
    page.get_by_role("button", name="Next steps to get help").click()
    expect(page.get_by_role("heading", name="Next steps to get help")).to_be_visible()
    expect(page.get_by_text(expected_text)).to_be_visible()


def test_discrimination_next_steps_page(page: Page):
    page.get_by_role("link", name="Discrimination").click()
    page.get_by_role("checkbox", name="School, college, university").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("checkbox", name="None of these").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("button", name="Next steps to get help").click()
    expect(page.get_by_role("heading", name="Next steps to get help")).to_be_visible()
    expect(
        page.get_by_text(
            "These organisations give free, independent advice for problems about discrimination."
        )
    ).to_be_visible()


def test_benefits_next_steps_page(page: Page):
    page.get_by_role("link", name="Benefits").click()
    page.get_by_role("radio", name="None of these").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("button", name="Next steps to get help").click()
    expect(page.get_by_role("heading", name="Next steps to get help")).to_be_visible()
    expect(
        page.get_by_text(
            "These organisations give free, independent advice for problems about benefits."
        )
    ).to_be_visible()
