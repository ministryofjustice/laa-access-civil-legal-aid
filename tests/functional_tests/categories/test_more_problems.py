from playwright.sync_api import Page, expect
import pytest


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize(
    "category_name, expected_heading, category",
    [
        pytest.param("Adopting a child from outside the UK", "Find a legal adviser", "mat"),
        pytest.param(
            "Appeal a decision that you cannot work with children or vulnerable adults",
            "Find a legal adviser",
            "",
        ),
        pytest.param(
            "Anti-social behaviour and gangs",
            "Were you accused by a landlord or the council?",
            "",
        ),
        pytest.param(
            "Clinical negligence in babies",
            "Find a legal adviser",
            "med",
        ),
        pytest.param(
            "Compensation for abuse, assault or neglect",
            "Find a legal adviser",
            "aap",
        ),
        pytest.param(
            "Domestic abuse - if you have been accused",
            "Legal aid is available for this type of problem",
            "",
        ),
        pytest.param(
            "Environmental pollution",
            "Find a legal adviser",
            "pub",
        ),
        pytest.param(
            "Female genital mutilation (FGM)",
            "Are you worried about someone's safety?",
            "",
        ),
        pytest.param(
            "Forced marriage",
            "Are you worried about someone's safety?",
            "",
        ),
        pytest.param(
            "Inquests for family members",
            "Find a legal adviser",
            "",
        ),
        pytest.param(
            "Mental health detention",
            "Find a legal adviser",
            "mhe",
        ),
        pytest.param(
            "Proceeds of Crime Act",
            "Find a legal adviser",
            "crm",
        ),
        pytest.param(
            "Terrorism",
            "Find a legal adviser",
            "immas",
        ),
        pytest.param(
            "Trafficking, modern slavery",
            "Find a legal adviser",
            "immas",
        ),
        pytest.param(
            "Next steps to get help",
            "Sorry, you’re not likely to get legal aid",
            "",
        ),
    ],
)
def test_more_problems(page: Page, category_name: str, expected_heading: str, category: str):
    page.get_by_role("link", name="More problems covered by legal aid").click()
    page.get_by_role("link", name=category_name).click()
    expect(page.get_by_role("heading", name=expected_heading)).to_be_visible()
    if len(category) > 0:
        if category_name == "Terrorism":
            assert page.url.endswith(f"find-a-legal-adviser?category={category}&secondary_category=pub")
        else:
            assert page.url.endswith(f"find-a-legal-adviser?category={category}")
