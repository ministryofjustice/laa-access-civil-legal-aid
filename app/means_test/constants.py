from enum import Enum


class EligibilityState(str, Enum):
    YES: str = "yes"
    NO: str = "no"
    UNKNOWN: str = "unknown"

    @classmethod
    def _missing_(cls, value):
        """Handle missing values by trying their lowercase equivalent or returning UNKNOWN if there is no match."""
        if isinstance(value, str):
            try:
                return cls(value.lower())
            except ValueError:
                return cls.UNKNOWN
        return None
