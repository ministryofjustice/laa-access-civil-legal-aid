import logging
import re

from wtforms.validators import ValidationError
from wtforms.validators import StopValidation

logger = logging.getLogger(__name__)

_URL_PATTERN = re.compile(r"https?://|www\.|/", re.IGNORECASE)


def sanitise_personalisation(value: str | None) -> str | None:
    """Strip whitespace and reject values containing URLs before sending to gov-notify."""
    if not value:
        return value
    value = value.strip()
    if _URL_PATTERN.search(value):
        logger.warning("Unsafe personalisation value blocked: %s", value[:50])
        return None
    return value


class ValidateDayTime:
    def __init__(self, day_field: str, message: bool = None):
        self.day_field = day_field
        self.message = message if message is not None else "Can not schedule a callback at the requested time"

    def __call__(self, form, field):
        selected_time = field.data
        selected_day = form._fields.get(self.day_field).data

        if not selected_day:
            #  Do not attempt to validate further, let this be handled by the selected day InputRequired validator.
            raise StopValidation()

        if selected_day not in form.time_slots:
            raise ValidationError(self.message)

        valid_time_slots = form.time_slots[selected_day]

        for time in valid_time_slots:
            if selected_time == time[0]:
                field.errors = []
                raise StopValidation()

        raise ValidationError(self.message)


class NoURLs:
    def __init__(self, message=None):
        self.message = message or "Enter a valid name"
        self._pattern = re.compile(r"https?://|www\.|/", re.IGNORECASE)

    def __call__(self, form, field):
        if field.data and self._pattern.search(field.data):
            raise ValidationError(self.message)


class ValidatePhoneNumber:
    def __init__(self, message=None):
        self.message = message or "Enter a valid phone number"
        self._allowed = re.compile(r"^[0-9+\s\-()\[\]]+$")

    def __call__(self, form, field):
        if not field.data:
            return
        if not self._allowed.match(field.data):
            raise ValidationError(self.message)
        digits = re.sub(r"\D", "", field.data)
        if not (7 <= len(digits) <= 15):
            raise ValidationError(self.message)
