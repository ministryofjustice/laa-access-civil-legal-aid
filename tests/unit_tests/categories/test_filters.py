from app.categories.filters import lowercase_category_name
from flask_babel import lazy_gettext as _
import pytest

TEST_CASES = [
    (
        _("Children, Families and Relationships"),
        _("children, families and relationships"),
    ),
    (_("Housing"), _("housing")),
    (_("Community care"), _("community care")),
    (_("Domestic Abuse"), _("domestic abuse")),
    (_("Welfare benefits"), _("welfare benefits")),
    (_("Discrimination"), _("discrimination")),
    (_("Mental health"), _("mental health")),
    (
        _("Special education needs and disability (SEND)"),
        _("special education needs and disability (send)"),
    ),
]


@pytest.mark.parametrize("category_name, expected", TEST_CASES)
def test_get_lowercase_category_name(category_name, expected):
    result = lowercase_category_name(category_name)
    assert result == expected
