from wtforms.validators import ValidationError
from wtforms.validators import StopValidation


class ValidateDayTime:
    def __init__(self, day_field: str, message: bool = None):
        self.day_field = day_field
        self.message = (
            message
            if message is not None
            else "Can not schedule a callback at the requested time"
        )

    def __call__(self, form, field):
        selected_time = field.data
        selected_day = form._fields.get(self.day_field).data

        valid_time_slots = form.time_slots[selected_day]

        for time in valid_time_slots:
            if selected_time == time:
                field.errors = []
                raise StopValidation()

        raise ValidationError(self.message)
