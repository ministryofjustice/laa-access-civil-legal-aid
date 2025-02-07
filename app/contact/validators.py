from wtforms.validators import Email, HostnameValidation
from enum import Enum
from wtforms.validators import StopValidation


class EmailValidator(Email):
    def __init__(self, message=None):
        # Ensure hostname validation is properly applied
        self.validate_hostname = HostnameValidation(require_tld=True)

        # Use WTForms' built-in email regex instead of a custom one
        super(EmailValidator, self).__init__(message=message)


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
