from flask_babel import lazy_gettext as _, LazyString
from dataclasses import dataclass


@dataclass
class Category:
    display_text: LazyString
    code: str
    article_category_name: str | None

    def __str__(self):
        # Returns the translated display text
        return str(self.display_text)


FAMILY = Category(_("Children, families and relationships"), "FAMILY", "Family")
HOUSING = Category(
    _("Housing, homelessness, losing your home"), "HOUSING", "Community care"
)
COMMUNITY_CARE = Category(_("Community care"), "COMMUNITY_CARE", "Community care")
DOMESTIC_ABUSE = Category(_("Domestic abuse"), "DOMESTIC_ABUSE", "Domestic abuse")
BENEFITS = Category(
    _("Appeal a decision about your benefits"), "BENEFITS", "Welfare benefits"
)
DISCRIMINATION = Category(_("Discrimination"), "DISCRIMINATION", "Discrimination")
MENTAL_CAPACITY = Category(
    _("Mental capacity, mental health"), "MENTAL_CAPACITY", "Mental health"
)
ASYLUM_AND_IMMIGRATION = Category(
    _("Asylum and immigration"), "ASYLUM_AND_IMMIGRATION", None
)
SOCIAL_CARE = Category(
    _("Care needs for disability and old age (social care)"), "SOCIAL_CARE", None
)
PUBLIC_LAW = Category(
    _("Legal action against police and public organisations"), "PUBLIC_LAW", "Public"
)
EDUCATION = Category(
    _("Special educational needs and disability (SEND)"), "EDUCATION", "Education"
)
