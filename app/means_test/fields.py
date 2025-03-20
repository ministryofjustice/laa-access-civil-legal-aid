import decimal
from decimal import Decimal, InvalidOperation

from flask import render_template
from flask_babel import lazy_gettext as _, LazyString
from wtforms.widgets import TextInput
from markupsafe import Markup
from wtforms import Field, IntegerField as BaseIntegerField, RadioField
from app.means_test.money_interval import MoneyInterval
import re
from app.means_test.validators import CurrencyValidator


class YesNoField(RadioField):
    def __init__(self, label: LazyString = None, validators=None, **kwargs):
        if "coerce" in kwargs:
            raise ValueError("The 'coerce' parameter is not allowed in a YesNoField")
        if "choices" in kwargs:
            raise ValueError(
                "Choices in a YesNoField are fixed and cannot be overridden"
            )
        choices = [(True, _("Yes")), (False, _("No"))]
        coerce = self._coerce_to_boolean
        super(YesNoField, self).__init__(
            label=label, validators=validators, choices=choices, coerce=coerce, **kwargs
        )  # noqa

    @staticmethod
    def _coerce_to_boolean(value):
        # Converts the string value from the HTML request to a boolean
        # "Yes" being True, "No" being False
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "y", "1", "t")
        return bool(value)

    @property
    def value(self):
        return _("Yes") if self.data else _("No")


class MoneyIntervalWidget(TextInput):
    def __call__(self, field, *args, **kwargs):
        # Pass the current values to the template
        return Markup(
            render_template(
                "means_test/components/money-field.html",
                field=field,
                value=field.value,
                interval=field.interval,
            )
        )


class MoneyIntervalField(Field):
    """
    A field that handles two separate text inputs.
    The raw data will contain both values separately.
    """

    @property
    def interval_choices(self):
        choices = [{"value": "", "text": _("-- Please select --")}]

        for value, item in self._intervals.items():
            choices.append(
                {
                    "value": value,
                    "text": item["label"],
                }
            )
        return choices

    @property
    def interval(self):
        return self.data["interval_period"]

    @property
    def value(self):
        value = self.data["per_interval_value_pounds"]
        if value is None:
            raw_value = (
                self.raw_data[0] if self.raw_data and len(self.raw_data) > 0 else None
            )
            value = raw_value
        return value

    def __init__(
        self,
        label=None,
        hint_text=None,
        validators=None,
        exclude_intervals=None,
        min_val=0,
        max_val=9999999999,
        **kwargs,
    ):
        super().__init__(label, validators, **kwargs)
        self.title = label
        self.hint_text = hint_text
        self.field_with_error = set()  # Contains a set of fields with errors so each field can be highlighted when required
        self._intervals = MoneyInterval._intervals.copy()
        self.min_val = min_val
        self.max_val = max_val
        if exclude_intervals:
            for interval in exclude_intervals:
                del self._intervals[interval]

    @property
    def data(self):
        if self._data is None:
            instance = MoneyInterval()
        elif isinstance(self._data, MoneyInterval):
            instance = self._data
        else:
            instance = MoneyInterval(self._data)
        return instance.to_json()

    @data.setter
    def data(self, data):
        self._data = data

    def process_formdata(self, valuelist):
        """Process the form data from both inputs"""
        if valuelist and len(valuelist) == 2:
            # Handle the data coming from the form fields named field.id[value] and field.id[interval]
            valuelist[0] = CurrencyValidator.clean_input(valuelist[0])
            self.data = valuelist

            if (
                "per_interval_value" not in self.data
                or self.data["per_interval_value"] is None
            ):
                return

            # Validate min/max
            if (
                self.min_val is not None
                and self.data["per_interval_value"] < self.min_val
            ):
                self.field_with_error.add("value")
                raise ValueError(
                    f"Enter a value of more than £{self.min_val / 100:,.2f}"
                )
            if (
                self.max_val is not None
                and self.data["per_interval_value"] > self.max_val
            ):
                self.field_with_error.add("value")
                raise ValueError(
                    f"Enter a value of less than £{self.max_val / 100:,.2f}"
                )

        elif valuelist and len(valuelist) == 1 and isinstance(valuelist[0], dict):
            # Data being restored from the session
            self.data = valuelist[0]


class MoneyField(BaseIntegerField):
    def __init__(
        self, label=None, validators=None, min_val=0, max_val=9999999999, **kwargs
    ):
        self._user_input = None
        self.data = None
        self.min_val = min_val
        self.max_val = max_val
        super(MoneyField, self).__init__(label, validators, **kwargs)

    @staticmethod
    def clean_input(value):
        # Remove pound sign (£), spaces, and commas from user input
        value = str(value)
        return re.sub(r"[£\s,]", "", value.strip())

    def process_formdata(self, valuelist):
        if valuelist and isinstance(valuelist[0], int):
            # The form is being restored from the session where the conversion has already taken place
            self.data = valuelist[0]
        elif valuelist:
            self._user_input = valuelist[0]

            # Clean the input
            clean_input = self.clean_input(valuelist[0])

            try:
                decimal_value = Decimal(clean_input)
            except (ValueError, InvalidOperation):
                raise ValueError("Enter a valid amount")

            # Check if value has more than 2 decimal places
            if decimal_value != decimal_value.quantize(
                Decimal(".01"), rounding=decimal.ROUND_DOWN
            ):
                raise ValueError("Enter a valid amount (maximum 2 decimal places)")

            self.data = int(decimal_value * 100)

            # Validate min/max
            if self.min_val is not None and self.data < self.min_val:
                raise ValueError(
                    f"Enter a value of more than £{self.min_val / 100:,.2f}"
                )

            if self.max_val is not None and self.data > self.max_val:
                raise ValueError(
                    f"Enter a value of less than £{self.max_val / 100:,.2f}"
                )

    def process_data(self, value):
        """Handle data coming from the database/code (in pence)"""
        if value is not None:
            self.data = value
            pounds = value // 100
            pence = value % 100
            self._user_input = f"{pounds:,}.{pence:02d}"

    def _value(self):
        """Format value for display"""
        if self._user_input is not None:
            return self._user_input
        if self.data is not None:
            pounds = self.data // 100
            pence = self.data % 100
            return f"{pounds:,}.{pence:02d}"
        return ""


class IntegerField(BaseIntegerField):
    def process_formdata(self, valuelist):
        """The parent method will fail when it tries to convert a None to an Integer"""
        if not valuelist or valuelist[0] is None:
            return

        super().process_formdata(valuelist)
