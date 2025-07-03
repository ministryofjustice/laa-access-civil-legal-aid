from flask import url_for
from app.main import bp
import json
from markupsafe import Markup
from markdown import markdown
from govuk_frontend_wtf.main import flatten_errors, merger
from flask_babel import lazy_gettext as _
from datetime import datetime, timedelta


@bp.app_template_filter("markdown")
def render_markdown(text, **kwargs):
    """Renders Markdown text as HTML, this can be invoked in Jinja templates using the markdown filter:
    {{ "# Hello, World!" | markdown }}
    We use markupsafe to ensure characters are escaped correctly so they can be safely rendered.
    """
    return Markup(markdown(text, **kwargs))


@bp.app_template_filter("dict")
def str_to_dict(s):
    """Uses the JSON module to parse a string into a dict.
    This can be invoked in Jinja templates using:
    {{ '{"spam": "eggs"}' | dict }}

    :param s: str
    :return: dict
    """
    return json.loads(s)


@bp.app_template_filter("get_item")
def get_item_from_dict(d, s):
    """Gets an item from a dict safely returning None if it is not present
    This can be invoked in Jinja templates using:
    {{ '{"spam": "eggs"}' | dict | get_item("spam") }}

    :param d: dict
    :param s: str
    :return: any
    """
    if s not in d:
        return None
    return d[s]


@bp.app_template_filter("category_url_for")
def category_url_for(data, **kwargs):
    if isinstance(data, dict):
        data = data.copy()
        endpoint = data.pop("endpoint", None)
        if endpoint is None:
            raise ValueError("No endpoint provided")
        url = url_for(endpoint, **data)
    else:
        url = url_for(data)
    return url


@bp.app_template_global()
def wtforms_errors(form, params={}):
    """An adapted version of the wtforms_errors function from the govuk_frontend_wtf package that marks the "There is a problem" text as translatable."""
    wtforms_params = {"titleText": _("There is a problem"), "errorList": []}

    id_map = {}
    for field_name in form._fields.keys():
        field = getattr(form, field_name, None)
        if field and hasattr(field, "id"):
            id_map[field_name] = field.id

    wtforms_params["errorList"] = flatten_errors(form.errors, id_map=id_map)

    return merger.merge(wtforms_params, params)


@bp.app_template_filter("format_time_12h")
def format_time_12h(time: datetime.time):
    """Formats time from 24-hour to 12-hour format with am/pm.

    Converts times like "09:00" to "9:00am" and "14:30" to "2:30pm"

    :param time_str: str - Time in HH:MM format
    :return: str - Time in 12-hour format with am/pm
    """

    # Format to 12-hour with am/pm
    formatted = time.strftime("%I:%M%p").lower()

    # Remove leading zero from hour (9:00am instead of 09:00am)
    if formatted.startswith("0"):
        formatted = formatted[1:]

    return formatted


@bp.app_template_filter("format_callback_time_slot")
def format_callback_time_slot(start_time):
    callback_duration = 30  # 30 minutes

    start_time = datetime.strptime(start_time, "%H:%M")
    end_time = start_time + timedelta(minutes=callback_duration)

    return f"{format_time_12h(start_time)} and {format_time_12h(end_time)}"
