from enum import Enum
from flask_babel import lazy_gettext as _


class Category(str, Enum):
    FAMILY = _("Children, families and relationships")
    HOUSING = _("Housing, homelessness, losing your home")
    COMMUNITY_CARE = _("Community care")
    DOMESTIC_ABUSE = _("Domestic abuse")
    BENEFITS = _("Appeal a decision about your benefits")
    DISCRIMINATION = _("Discrimination")
    MENTAL_CAPACITY = _("Mental capacity, mental health")
    ASYLUM_AND_IMMIGRATION = _("Asylum and immigration")
    SOCIAL_CARE = _("Care needs for disability and old age (social care)")
    PUBLIC_LAW = _("Legal action against police and public organisations")
    EDUCATION = _("Special educational needs and disability (SEND)")


def get_category_from_display_text(display_text: str) -> Category | None:
    """Convert a category display text back to its corresponding Category enum value.

    Args:
        display_text (str): The display text to convert back to a Category enum.
                           This should match one of the translated strings defined
                           in the Category enum.

    Returns:
        Category or None: The corresponding Category enum value if found,
                          None if no matching category is found.
    """
    reverse_mapping = {str(category.value): category for category in Category}

    # Attempt to find the category enum value for the given display text
    # Return None if no matching category is found
    return reverse_mapping.get(display_text)


def article_category(category_display_text: str):
    """Returns the CLA_Backend article category name for a given category
    This is used to populate the alternative help organisations
    """
    category = get_category_from_display_text(category_display_text)
    mapping = {
        Category.HOUSING: _("Housing"),
        Category.COMMUNITY_CARE: _("Community care"),
        Category.FAMILY: _("Family"),
        Category.DOMESTIC_ABUSE: _("Domestic abuse"),
        Category.BENEFITS: _("Welfare benefits"),
        Category.DISCRIMINATION: _("Discrimination"),
        Category.MENTAL_CAPACITY: _("Mental health"),
        Category.PUBLIC_LAW: _("Public"),
        Category.EDUCATION: _("Education"),
    }
    if category not in mapping:
        return None
    return mapping[category]
