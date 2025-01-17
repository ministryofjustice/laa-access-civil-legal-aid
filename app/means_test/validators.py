from flask import session
from wtforms.validators import StopValidation


class ValidateIf:
    def __init__(
        self,
        dependent_field_name: str,
        dependent_field_value,
    ):
        self.dependent_field_name: str = dependent_field_name
        self.dependent_field_value = dependent_field_value

    def __call__(self, form, field):
        other_field = form._fields.get(self.dependent_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.dependent_field_name)

        # If the dependent field doesn't match the value, skip validation
        if other_field.data != self.dependent_field_value:
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
        amount = field.value or None
        interval = field.interval or None
        print("VALIDATOR")
        print(amount)
        print(interval)
        print("-----")

        if (not amount) and (not interval):
            message = messages["message"]
            field.errors.append(message)
            field.field_with_error.extend(["value", "interval"])
            return False
        if not amount:
            message = messages["amount_message"]
            field.field_with_error.append("value")
            field.errors.append(message)
            return False
        if not interval:
            message = messages["freq_message"]
            field.field_with_error.append("interval")
            field.errors.append(message)
            return False
