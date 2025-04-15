from enum import Enum


class EligibilityState(str, Enum):
    YES: str = "yes"
    NO: str = "no"
    UNKNOWN: str = "unknown"

    @classmethod
    def _missing_(cls, value):
        """Handle missing values by trying their lowercase equivalent or returning UNKNOWN if there is no match."""
        if isinstance(value, str):
            lower_value = value.lower()
            for member in cls:
                if member.value == lower_value:
                    return member
            return cls.UNKNOWN
        return None

    def __bool__(self):
        return self == self.YES
