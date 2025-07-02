from decimal import Decimal


def pence_to_pounds(value: int):
    if not isinstance(value, int):
        raise ValueError(f"Cannot convert type: {type(value)} to pence.")
    decimal_value = (Decimal(value) / 100).quantize(Decimal(".01"))
    return float(decimal_value)


def none_filter(array):
    return [x for x in array if x is not None]
