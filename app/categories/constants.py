from flask_babel import lazy_gettext as _, LazyString
from dataclasses import dataclass


@dataclass
class Category:
    display_text: LazyString
    code: str
    article_category_name: str | None
    chs_code: str | None  # One of legalaid_categories.code

    def __str__(self):
        # Returns the translated display text
        return str(self.display_text)


FAMILY = Category(
    _("Children, families and relationships"), "FAMILY", "Family", "family"
)
HOUSING = Category(
    _("Housing, homelessness, losing your home"), "HOUSING", "Housing", "housing"
)
COMMUNITY_CARE = Category(
    _("Community care"), "COMMUNITY_CARE", "Community care", "commcare"
)
DOMESTIC_ABUSE = Category(
    _("Domestic abuse"), "DOMESTIC_ABUSE", "Domestic abuse", "family"
)
BENEFITS = Category(
    _("Appeal a decision about your benefits"),
    "BENEFITS",
    "Welfare benefits",
    "benefits",
)
DISCRIMINATION = Category(
    _("Discrimination"), "DISCRIMINATION", "Discrimination", "discrimination"
)
MENTAL_CAPACITY = Category(
    _("Mental capacity, mental health"),
    "MENTAL_CAPACITY",
    "Mental health",
    "mentalhealth",
)
ASYLUM_AND_IMMIGRATION = Category(
    _("Asylum and immigration"), "ASYLUM_AND_IMMIGRATION", None, "immigration"
)
SOCIAL_CARE = Category(
    _("Care needs for disability and old age (social care)"),
    "SOCIAL_CARE",
    None,
    "commcare",
)
PUBLIC_LAW = Category(
    _("Legal action against police and public organisations"),
    "PUBLIC_LAW",
    "Public",
    "publiclaw",
)
EDUCATION = Category(
    _("Special educational needs and disability (SEND)"),
    "EDUCATION",
    "Education",
    "education",
)
