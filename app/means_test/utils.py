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
                self.amount = value[0]
                self.interval = value[1]

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

        try:
            self["per_interval_value"] = to_amount(value)

        except (InvalidOperation, ValueError):
            raise ValueError(
                "Invalid value for amount {0} ({1})".format(value, type(value))
            )

    def amount_to_pounds(self):
        if not self["per_interval_value"]:
            return None
        return int(self["per_interval_value"] / 100)

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
        if self.amount is None or self.interval == "":
            return MoneyInterval(0)

        if self.interval == "per_month":
            return self

        multiplier = self._intervals[self.interval]["multiply_factor"]

        return MoneyInterval(int(self.amount * multiplier))

    def to_json(self):
        return {
            "per_interval_value": self.amount,
            "interval_period": self.interval,
        }
