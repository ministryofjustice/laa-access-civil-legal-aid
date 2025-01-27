from flask import render_template
from wtforms.widgets import TextInput
from markupsafe import Markup
from wtforms import Field
from flask_babel import lazy_gettext as _
from app.means_test.money_interval import MoneyInterval


class MoneyFieldWidget(TextInput):
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


class MoneyField(Field):
    """
    A field that handles two separate text inputs.
    The raw data will contain both values separately.
    """

    _intervals = {
        "": _("-- Please select --"),
        "per_week": _("each week"),
        "per_4week": _("every 4 weeks"),
        "per_month": _("each month"),
        "per_year": _("each year"),
    }

    @property
    def interval_choices(self):
        choices = []
        for value, text in self._intervals.items():
            choices.append(
                {
                    "value": value,
                    "text": text,
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
        self._intervals = self._intervals.copy()
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
