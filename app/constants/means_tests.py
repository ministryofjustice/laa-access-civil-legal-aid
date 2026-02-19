# Shared constants for means tests. So that they can be used in both the API and the front end without circular imports.
from enum import Enum


class IneligibleReason(str, Enum):
    GROSS_INCOME = "gross_income"
    DISPOSABLE_INCOME = "disposable_income"
    CAPITAL = "capital"
