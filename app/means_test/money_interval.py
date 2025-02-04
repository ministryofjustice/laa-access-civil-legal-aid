from decimal import Decimal, InvalidOperation
from flask_babel import lazy_gettext as _


def to_amount(value):
    amount = None

    if value is None:
        amount = None

    elif isinstance(value, str):
        amount = to_amount(Decimal(value.replace(",", "").replace(" ", "")))

    elif isinstance(value, float):
        amount = int(value * 100)

    elif isinstance(value, Decimal):
        amount = int(value * 100)

    else:
        amount = int(value)

    return amount


class MoneyInterval(dict):
    # interval_name, user_copy_name, multiply_factor (to get monthly value)
    _intervals = {
        "per_week": {"label": _("per week"), "multiply_factor": 52.0 / 12.0},
        "per_2week": {"label": _("2 weekly"), "multiply_factor": 26.0 / 12.0},
        "per_4week": {"label": _("4 weekly"), "multiply_factor": 13.0 / 12.0},
        "per_month": {"label": _("per month"), "multiply_factor": 1.0},
        "per_year": {"label": _("per year"), "multiply_factor": 1.0 / 12.0},
    }

    def __init__(self, *args, **kwargs):
        super(MoneyInterval, self).__init__(
            {"per_interval_value": None, "interval_period": None}
        )

        if len(args) > 0:
            value = args[0]
            if isinstance(value, MoneyInterval):
                self.amount = value.amount
                self.interval = value.interval
            elif isinstance(value, dict):
                self.amount = value.get("per_interval_value")
                if "interval_period" in value:
                    interval = value.get("interval_period")
                    if interval:
                        self.interval = interval
            elif isinstance(value, list):
                if value[0]:
                    self.amount = value[0]
                if value[1]:
                    self.interval = value[1]
            else:
                self.amount = value
                self.interval = "per_month"

        else:
            self.amount = kwargs.get("per_interval_value")
            self.interval = kwargs.get("interval_period")

    @property
    def amount(self):
        return self.get("per_interval_value")

    @amount.setter
    def amount(self, value):
        """
        Assumes integer is amount in pence, float or Decimal is amount in
        pounds and first 2 decimal places are pence. String is converted to
        Decimal first.
        """

        # If you have an amount of 0 the interval is irrelevant, therefore default to per_month
        # This allows the user to leave frequency as "--Please select--" and enter 0 for the amount
        if self.interval is None and value == "0":
            self.interval = "per_month"

        try:
            self["per_interval_value"] = to_amount(value)

        except (InvalidOperation, ValueError):
            raise ValueError(
                "Invalid value for amount {0} ({1})".format(value, type(value))
            )

    def amount_to_pounds(self):
        if not self["per_interval_value"]:
            return None
        return self["per_interval_value"] / 100

    @property
    def interval(self):
        return self.get("interval_period")

    @interval.setter
    def interval(self, value):
        if value:
            if value in MoneyInterval._intervals:
                self["interval_period"] = value
            else:
                raise ValueError(value)

    def per_month(self):
        if self.amount is None or self.interval is None:
            return MoneyInterval(0)

        if self.interval == "per_month":
            return self

        multiplier = self._intervals[self.interval]["multiply_factor"]

        return MoneyInterval(int(self.amount * multiplier))

    def to_json(self):
        return {
            "per_interval_value": self.amount,
            "per_interval_value_pounds": self.amount_to_pounds(),
            "interval_period": self.interval,
        }

    def __add__(self, other):
        if other == 0:
            other = MoneyInterval(0)

        if not isinstance(other, MoneyInterval):
            if self.is_money_interval(other):
                other = MoneyInterval(other)
            else:
                raise ValueError(other)

        first = self.per_month()
        second = other.per_month()

        return MoneyInterval(first.amount + second.amount)

    def __radd__(self, other):
        return self.__add__(other)

    @classmethod
    def is_money_interval(cls, other):
        if hasattr(other, "keys") and callable(other.keys):
            keys = set(other.keys())
            return keys == set(["per_interval_value", "interval_period"])
        return False
