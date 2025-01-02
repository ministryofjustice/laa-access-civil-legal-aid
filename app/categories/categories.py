from enum import Enum
from flask_babel import lazy_gettext as _


class Category(str, Enum):
    HOUSING = _("Housing")
    DEBT = _("Debt")
    EMPLOYMENT = _("Employment")
    COMMUNITY_CARE = _("Community care")
    FAMILY = _("Family")
    DOMESTIC_ABUSE = _("Domestic abuse")
    BENEFITS = _("Welfare Benefits")
    DISCRIMINATION = _("Discrimination")
    MENTAL_CAPACITY = _("Mental capacity, mental health")
    PUBLIC = _("Legal action against public organisations")
    SEND = _("SEND")
