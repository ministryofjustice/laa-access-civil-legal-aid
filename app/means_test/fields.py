from flask import render_template
from wtforms.widgets import TextInput
from markupsafe import Markup
from wtforms import Field
from flask_babel import lazy_gettext as _
from app.means_test.utils import MoneyInterval


class MoneyFieldWidgetWidget(TextInput):
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
        self.hint = hint_text
        self.value = None  # Amount
        self.interval = None  # Frequency
        self.field_with_error = []
        self._intervals = self._intervals.copy()
        if exclude_intervals:
            for interval in exclude_intervals:
                del self._intervals[interval]

    @property
    def data(self):
        if self._data is None:
            return MoneyInterval()
        elif isinstance(self._data, MoneyInterval):
            return self._data
        else:
            return MoneyInterval(self._data)

    @data.setter
    def data(self, data):
        self._data = data

    def process_formdata(self, valuelist):
        """Process the form data from both inputs"""
        if valuelist and len(valuelist) == 2:
            # Handle the data coming from the form fields named field.id[value] and field.id[interval]
            self.value = valuelist[0]
            self.interval = valuelist[1]
            self.data = valuelist

    def validate(self, form, extra_validators=None):
        if self.interval and self.interval not in self._intervals:
            raise ValueError(
                f"Invalid {self.interval} interval value given for field {self.name}"
            )
        return super().validate(form, extra_validators)
