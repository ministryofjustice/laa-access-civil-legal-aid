from decimal import Decimal

from app.means_test.money_interval import MoneyInterval


def pence_to_pounds(value: MoneyInterval | int):
    if isinstance(value, MoneyInterval):
        value = value.per_month().amount
    decimal_value = (Decimal(value) / 100).quantize(Decimal(".01"))
    return float(decimal_value)


def none_filter(array):
    return [x for x in array if x is not None]
