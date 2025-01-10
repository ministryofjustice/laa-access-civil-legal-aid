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
