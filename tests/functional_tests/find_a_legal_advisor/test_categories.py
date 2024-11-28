import pytest
from playwright.sync_api import Page, expect
from typing import Dict, Optional
from flask import url_for
import re

CATEGORIES = [
    {"code": "MOSL", "name": "Modern slavery", "info_text": None},
    {
        "code": "MED",
        "name": "Clinical negligence",
        "info_text": "You will usually only get legal aid for advice about clinical negligence if your child has suffered a brain injury during pregnancy",
    },
    {"code": "PUB", "name": "Public law", "info_text": None},
    {"code": "MHE", "name": "Mental health", "info_text": None},
    {"code": "COM", "name": "Community care", "info_text": None},
    {"code": "DEB", "name": "Debt", "info_text": None},
    {
        "code": "WB",
        "name": "Welfare benefits",
        "info_text": "Civil Legal Advice does not provide advice about issues related to welfare benefits",
    },
    {
        "code": "HLPAS",
        "name": "the Housing Loss Prevention Advice Service",
        "info_text": None,
    },
    {"code": "FMED", "name": "Family mediation", "info_text": None},
    {"code": "DISC", "name": "Discrimination", "info_text": None},
    {"code": "AAP", "name": "Claims Against Public Authorities", "info_text": None},
    {"code": "EDU", "name": "Education", "info_text": None},
    {"code": "MAT", "name": "Family", "info_text": None},
    {"code": "IMMAS", "name": "Immigration or asylum", "info_text": None},
    {"code": "HOU", "name": "Housing", "info_text": None},
    {"code": "PL", "name": "Prison law", "info_text": None},
    {"code": "CRM", "name": "Crime", "info_text": None},
]


@pytest.mark.usefixtures("live_server")
class TestLegalAdvisorCategories:
    @pytest.mark.parametrize("category", CATEGORIES)
    def test_category_search(
        self, page: Page, category: Dict[str, Optional[str]]
    ) -> None:
        """Test that each category shows the correct header text and additional information if applicable"""
        page.goto(
            url_for(
                "find-a-legal-advisor.search",
                category=category["code"].lower(),
                _external=True,
            )
        )

        # Check category text is visible
        expect(page.get_by_text(f"For {category['name'].lower()}")).to_be_visible()

        # Check for category-specific information if it exists
        if category["info_text"]:
            expect(page.get_by_text(category["info_text"], exact=False)).to_be_visible()

        # Fill in postcode and search
        page.get_by_label("Postcode").click()
        page.get_by_label("Postcode").fill("SW1A")
        page.get_by_role("button", name="Search").click()

        # Verify category text and information remain visible after search
        expect(page.get_by_text(f"For {category['name'].lower()}")).to_be_visible()
        if category["info_text"]:
            expect(page.get_by_text(category["info_text"], exact=False)).to_be_visible()


@pytest.mark.usefixtures("live_server")
class TestCategoriesURL:
    def test_multi_category_url(self, page: Page) -> None:
        # Select the mental health category
        page.get_by_role("link", name="Mental capacity, mental health").click()
        expect(page.get_by_text("For mental health")).to_be_visible()

        # Get the url and assert there are 2 categories
        expect(page).to_have_url(re.compile(".*category=mhe&secondary_category=com*.*"))

        # Fill in postcode and search
        page.get_by_label("Postcode").fill("SW1A")
        page.get_by_role("button", name="Search").click()

        # Verify category is displayed in the next page
        expect(page.get_by_text("For mental health")).to_be_visible()
        expect(page).to_have_url(re.compile(".*category=mhe&secondary_category=com*.*"))

        # Click the second page to ensure url is carried over
        page.get_by_role("link", name="2").click()
        expect(page.get_by_text("For mental health")).to_be_visible()
        expect(page).to_have_url(re.compile(".*category=mhe&secondary_category=com*.*"))

    def test_single_category_url(self, page: Page) -> None:
        # Select more problems and clinical negligence
        page.get_by_role("button", name="More problems covered by legal aid").click()
        expect(
            page.get_by_role("link", name="Clinical negligence in babies")
        ).to_be_visible()
        page.get_by_role("link", name="Clinical negligence in babies").click()
        expect(page.get_by_text("For clinical negligence")).to_be_visible()

        # Get the url and assert there is 1 category
        expect(page).to_have_url(re.compile(".*category=med"))

        # Fill in postcode and search
        page.get_by_label("Postcode").fill("SW1A")
        page.get_by_role("button", name="Search").click()

        # Verify category is displayed in the next page
        expect(page.get_by_text("For clinical negligenc")).to_be_visible()
        expect(page).to_have_url(re.compile(".*category=med"))
