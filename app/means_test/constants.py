from enum import Enum


class EligibilityResult(Enum):
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    UNKNOWN = "unknown"  # Represents the fact that we do not have enough information to determine the users' financial eligibility.

    @classmethod
    def from_string(cls, value):
        value_mapping = {
            "yes": cls.ELIGIBLE,
            "no": cls.INELIGIBLE,
            "unknown": cls.UNKNOWN,
        }
        return value_mapping.get(value, cls.UNKNOWN)

    def __bool__(self):
        return self == self.ELIGIBLE
