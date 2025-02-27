from wtforms.validators import ValidationError


class ExclusiveValue:
    """Validator to ensure that if an exclusive choice is selected, no other options can be selected, and vice versa.
    This is typically used to validate that "None of these" cannot be selected along with another option.
    """

    def __init__(self, exclusive_value: str = None, message: str = None):
        self.message = message or "Invalid choice"
        self.exclusive_value = exclusive_value or "none"

    def __call__(self, form, field):
        if not field.data:
            return

        selected_values = set(field.data)

        # Check if the exclusive_value is selected along with other options
        if self.exclusive_value in selected_values and len(selected_values) > 1:
            raise ValidationError(self.message)
