from enum import Enum
from flask_babel import lazy_gettext as _


class Category(str, Enum):
    # This is an incomplete list of categories, aligning with those found on CLA_Public
    # the full authoritative list will come from design team
    HOUSING = _("Housing")
    DEBT = _("Debt")
    EMPLOYMENT = _("Employment")
    COMMUNITY_CARE = _("Community care")
    FAMILY = _("Family")
    DOMESTIC_ABUSE = _("Domestic abuse")
    BENEFITS = _("Welfare Benefits")
    DISCRIMINATION = _("Discrimination")
    MENTAL_CAPACITY = _("Mental health")
    IMMIGRATION_AND_ASYLUM = _("Immigration and asylum")
    PUBLIC_LAW = _("Public law")
    EDUCATION = _("Education")
