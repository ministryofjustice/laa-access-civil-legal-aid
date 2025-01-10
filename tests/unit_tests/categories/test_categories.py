from app.categories.constants import (
    Category,
    get_category_from_display_text,
    get_article_category_name,
)


def test_get_category_from_display_text():
    result = get_category_from_display_text("Housing, homelessness, losing your home")
    assert result == Category.HOUSING

    result = get_category_from_display_text("InvalidCategory")
    assert result is None, "Should return None for invalid category"

    result = get_category_from_display_text(None)
    assert result is None


def test_article_category():
    result = get_article_category_name("Housing, homelessness, losing your home")
    assert result == "Housing"

    result = get_article_category_name("InvalidCategory")
    assert result is None

    result = get_article_category_name(None)
    assert result is None
