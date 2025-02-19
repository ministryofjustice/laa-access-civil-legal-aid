from flask_babel import lazy_gettext as _, LazyString
from app.categories.constants import EDUCATION
from app.categories import bp


@bp.app_template_filter("lowercase_category_name")
def lowercase_category_name(category_name: LazyString) -> LazyString:
    """Gets the lowercase variant of the translatable category name"""
    if category_name == EDUCATION.display_text:
        return _("special educational needs and disability (SEND)")
    return category_name.lower()
