from wtforms.validators import ValidationError
from email_validator import validate_email, EmailNotValidError
from enum import Enum
from wtforms.validators import StopValidation


class EmailValidator:
    def __init__(self, message=None):
        if not message:
            message = "Invalid email address."
        self.message = message

    def __call__(self, form, field):
        try:
            validate_email(field.data, check_deliverability=True)
        except EmailNotValidError:
            raise ValidationError(self.message)


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
            raise ValueError(f'No field named "{self.dependent_field_name}" in form.')

        # If the dependent field is a SelectMultipleField, its data will be a list
        dependent_data = other_field.data

        # Update the condition check logic to handle lists
        if isinstance(dependent_data, list):
            # If using `IN` condition, check if dependent_value is in the list
            if self.condition_type == ValidateIfType.IN:
                match = self.dependent_field_value in dependent_data
            # If using `EQ` condition, check if there's a match
            elif self.condition_type == ValidateIfType.EQ:
                match = self.dependent_field_value in dependent_data
            else:
                match = False
        else:
            # If the dependent data is not a list, use the same logic
            match = self.condition_type(self.dependent_field_value, dependent_data)

        if not match:
            field.errors = []
            raise StopValidation()
