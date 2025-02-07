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
    display_text=_("Children, families and relationships"),
    code="FAMILY",
    article_category_name="Family",
    chs_code="family",
)
HOUSING = Category(
    display_text=_("Housing, homelessness, losing your home"),
    code="HOUSING",
    article_category_name="Housing",
    chs_code="housing",
)
COMMUNITY_CARE = Category(
    display_text=_("Community care"),
    code="COMMUNITY_CARE",
    article_category_name="Community care",
    chs_code="commcare",
)
DOMESTIC_ABUSE = Category(
    display_text=_("Domestic abuse"),
    code="DOMESTIC_ABUSE",
    article_category_name="Domestic Abuse",
    chs_code="family",
)
BENEFITS = Category(
    display_text=_("Welfare benefits"),
    code="BENEFITS",
    article_category_name="Welfare benefits",
    chs_code="benefits",
)
DISCRIMINATION = Category(
    display_text=_("Discrimination"),
    code="DISCRIMINATION",
    article_category_name="Discrimination",
    chs_code="discrimination",
)
MENTAL_CAPACITY = Category(
    display_text=_("Mental capacity, mental health"),
    code="MENTAL_CAPACITY",
    article_category_name="Mental health",
    chs_code="mentalhealth",
)
ASYLUM_AND_IMMIGRATION = Category(
    display_text=_("Asylum and immigration"),
    code="ASYLUM_AND_IMMIGRATION",
    article_category_name=None,
    chs_code="immigration",
)
SOCIAL_CARE = Category(
    display_text=_("Care needs for disability and old age (social care)"),
    code="SOCIAL_CARE",
    article_category_name=None,
    chs_code="commcare",
)
PUBLIC_LAW = Category(
    display_text=_("Legal action against police and public organisations"),
    code="PUBLIC_LAW",
    article_category_name="Public",
    chs_code="publiclaw",
)
EDUCATION = Category(
    display_text=_("Special educational needs and disability (SEND)"),
    code="EDUCATION",
    article_category_name="Education",
    chs_code="education",
)
