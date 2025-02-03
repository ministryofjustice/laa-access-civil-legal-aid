import decimal
import re
from decimal import Decimal, InvalidOperation
from enum import Enum
from flask import session
from wtforms.validators import StopValidation


class ValidateIfType(Enum):
    IN: str = lambda x, items: x in items
    EQ: str = lambda a, b: a == b


class ValidateIf:
    def __init__(
        self,
        dependent_field_name: str,
        dependent_field_value,
        condition_type: ValidateIfType = ValidateIfType.EQ,
    ):
        self.dependent_field_name: str = dependent_field_name
        self.dependent_field_value = dependent_field_value
        self.condition_type: ValidateIfType = condition_type

    def __call__(self, form, field):
        other_field = form._fields.get(self.dependent_field_name)
        if other_field is None:
            raise ValueError('no field named "%s" in form' % self.dependent_field_name)

        # If the dependent field doesn't match the value, skip validation
        match = self.condition_type(self.dependent_field_value, other_field.data)
        if not match:
            field.errors = []
            raise StopValidation()


class ValidateIfSession:
    def __init__(
        self,
        property_name: str,
        property_value: str,
    ):
        self.property_name: str = property_name
        self.property_value: str = property_value

    def __call__(self, form, field):
        eligibility = session.get_eligibility()
        session_value = getattr(eligibility, self.property_name)

        if session_value is None:
            raise ValueError(f"{self.property_name} does not exist in session")

        if session_value != self.property_value:
            field.errors = []
            raise StopValidation()


class MoneyIntervalAmountRequired(object):
    def __init__(self, message=None, freq_message=None, amount_message=None, **kwargs):
        self.messages = {
            "message": message,
            "freq_message": freq_message,
            "amount_message": amount_message,
        }
        self.partner_messages = {
            "message": kwargs.get("partner_message", message),
            "freq_message": kwargs.get("partner_freq_message", freq_message),
            "amount_message": kwargs.get("partner_amount_message", amount_message),
        }

    def __call__(self, form, field):
        messages = self.messages
        amount = field.raw_data[0] if len(field.raw_data) > 0 else None
        interval = field.raw_data[1] if len(field.raw_data) > 1 else None

        try:
            CurrencyValidator.validate_currency(amount)
        except ValueError as e:
            field.errors.append(str(e))
            field.field_with_error.add("value")

        if (not amount or amount == "0") and (not interval or interval == ""):
            return

        if (not amount) and (not interval):
            message = messages["message"]
            field.errors.append(message)
            field.field_with_error.update({"value", "interval"})
            return False

        if not amount:
            message = messages["amount_message"]
            field.field_with_error.add("value")
            field.errors.append(message)
            return False

        if not interval or interval not in field._intervals:
            message = messages["freq_message"]
            field.field_with_error.add("interval")
            field.errors.append(message)
            return False


class CurrencyValidator:
    @staticmethod
    def clean_input(value):
        value = str(value)
        return re.sub(r"[£\s,]", "", value.strip())

    @staticmethod
    def validate_currency(value: str | None) -> Decimal | None:
        if not value:
            return None

        clean_input = CurrencyValidator.clean_input(value)

        try:
            decimal_value = Decimal(clean_input)
        except (ValueError, InvalidOperation):
            raise ValueError("Enter a number")

        # Check that the value has no more than 2 decimal places
        if decimal_value != decimal_value.quantize(
            Decimal(".01"), rounding=decimal.ROUND_DOWN
        ):
            raise ValueError("Enter a valid amount (maximum 2 decimal places)")

        return decimal_value
