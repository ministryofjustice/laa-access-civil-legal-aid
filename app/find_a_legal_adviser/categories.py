from enum import Enum


class FALACategory(Enum):
    MODERN_SLAVERY = "MOSL"
    CLINICAL_NEGLIGENCE = "MED"
    PUBLIC_LAW = "PUB"
    MENTAL_HEALTH = "MHE"
    COMMUNITY_CARE = "COM"
    DEBT = "DEB"
    WELFARE_BENEFITS = "WB"
    HOUSING_LOSS_PREVENTION_ADVICE_SERVICE = "HLPAS"
    FAMILY_MEDIATION = "FMED"
    DISCRIMINATION = "DISC"
    CLAIMS_AGAINST_PUBLIC_AUTHORITIES = "AAP"
    EDUCATION = "EDU"
    FAMILY = "MAT"
    IMMIGRATION_OR_ASYLUM = "IMMAS"
    HOUSING = "HOU"
    PRISON_LAW = "PL"
    CRIME = "CRM"

    @classmethod
    def is_valid_category(cls, value: str) -> bool:
        """
        Check if the provided value is a valid FALA category code, case-insensitively.

        Args:
            value: The category code to validate

        Returns:
            bool: True if the value is a valid category code, False otherwise
        """
        if not value:
            return False

        return any(category.value.upper() == value.upper() for category in cls)

    @classmethod
    def get_category_code(cls, category_name: str) -> str | None:
        """
        Returns the category code for a given category name.

        Args:
            category_name (str): The category name to look up

        Returns:
            str: The corresponding category code if found, None if not found
        """
        if not category_name:
            return None

        # Make comparison case-insensitive
        normalized_name = category_name.upper().replace(" ", "_")

        try:
            enum_member = cls[normalized_name]
            return enum_member.value
        except KeyError:
            return None
