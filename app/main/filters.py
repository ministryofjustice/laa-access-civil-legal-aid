from app.main import bp
import json
from markupsafe import Markup
from markdown import markdown


@bp.app_template_filter("markdown")
def render_markdown(text):
    """Renders Markdown text as HTML, this can be invoked in Jinja templates using the markdown filter:
    {{ "# Hello, World!" | markdown }}
    We use markupsafe to ensure characters are escaped correctly so they can be safely rendered.
    """
    return Markup(markdown(text))


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
