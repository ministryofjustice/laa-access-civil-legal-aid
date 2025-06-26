from datetime import datetime, timedelta
from app.contact_backup import bp


@bp.app_template_filter("format_callback_time")
def format_callback_time(start_time: datetime, callback_duration: timedelta = timedelta(minutes=30)) -> str | None:
    """Helper function to format the callback time string.

    Returns:
        str | None: formatted callback time string in the form of "Friday, 3 January at 09:00 - 09:30"
    """
    if not start_time or not isinstance(start_time, datetime):
        return None
    end_time = start_time + callback_duration

    formatted_start_date = start_time.strftime("%A, %-d %B at %H:%M")  # E.g. Monday, 1 January at 09:00
    formatted_end_time = end_time.strftime("%H:%M")  # E.g. 09:30

    return f"{formatted_start_date} - {formatted_end_time}"
