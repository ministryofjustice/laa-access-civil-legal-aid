from flask import render_template
from flask_babel import lazy_gettext as _
from wtforms.widgets import TextInput
from markupsafe import Markup
from wtforms import Field, IntegerField
from app.means_test.money_interval import MoneyInterval
import re


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
        return self.data["per_interval_value_pounds"]

    def __init__(
        self,
        label=None,
        hint_text=None,
        validators=None,
        exclude_intervals=None,
        **kwargs,
    ):
        super().__init__(label, validators, **kwargs)
        self.title = label
        self.hint_text = hint_text
        self.field_with_error = []
        self._intervals = MoneyInterval._intervals.copy()
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
            self.data = valuelist
        elif valuelist and len(valuelist) == 1 and isinstance(valuelist[0], dict):
            # Data being restored from the session
            self.data = valuelist[0]


class MoneyField(IntegerField):
    widget = TextInput()

    def __init__(
        self, label=None, validators=None, min_val=0, max_val=9999999999, **kwargs
    ):
        super(MoneyField, self).__init__(label, validators, **kwargs)
        self.min_val = min_val
        self.max_val = max_val

    def extract_pounds_and_pence(self, valuelist):
        pounds, _, pence = valuelist[0].strip().partition(".")
        try:
            pounds = pounds.decode("utf-8")
        except UnicodeEncodeError:
            # Input is already in UTF-8 format
            pass

        # xa3 is the ASCII character reference for the pound sign
        pounds = re.sub(r"^\xa3|[\s,]+", "", pounds)
        return pounds, pence

    def set_zero(self):
        self.data = 0

    def process_formdata(self, valuelist):
        if valuelist:
            pounds, pence = self.extract_pounds_and_pence(valuelist)

            if pence:
                if len(pence) > 2:
                    self.data = None
                    raise ValueError(self.gettext("Enter a number"))

                if len(pence) == 1:
                    pence = "{0}0".format(pence)

            try:
                self.data = int(pounds) * 100
                if pence:
                    self.data += int(pence)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext("Enter a number"))

            if self.min_val is not None and self.data < self.min_val:
                self.data = None
                raise ValueError(
                    self.gettext("Enter a value of more than £{:,.0f}").format(
                        self.min_val / 100.0
                    )
                )

            if self.max_val is not None and self.data > self.max_val:
                self.data = None
                raise ValueError(
                    self.gettext("Enter a value of less than £{:,.0f}").format(
                        self.max_val / 100.0
                    )
                )

    def process_data(self, value):
        self.data = value
        if value:
            pence = value % 100
            pounds = value / 100
            self.data = "{0:,}.{1:02}".format(pounds, pence)
