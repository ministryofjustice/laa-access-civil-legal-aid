import pytest
from unittest.mock import patch
from app.categories.constants import HOUSING, ASYLUM_AND_IMMIGRATION
from app.categories.results.views import ResultPage


@pytest.fixture
def mock_organisations():
    return [
        {"name": "Shelter", "url": "http://shelter.org.uk"},
        {"name": "Housing Rights", "url": "http://housingrights.org.uk"},
    ]


def test_get_context_with_housing_category(mock_organisations):
    with (
        patch(
            "app.categories.results.views.cla_backend.get_help_organisations",
            return_value=mock_organisations,
        ) as mock_get_orgs,
        patch(
            "app.categories.results.views.get_fala_category_code", return_value="HOU"
        ),
    ):
        view = ResultPage(template="categories/results/housing.html")
        result = view.get_context(category=HOUSING)

        assert result["category_name"] == "Housing, homelessness, losing your home"
        assert result["organisations"] == mock_organisations
        assert result["fala_category_code"] == "HOU"

        # Verify correct article_category_name was used
        mock_get_orgs.assert_called_once_with("Housing")


def test_get_context_with_immigration_category():
    with (
        patch(
            "app.categories.results.views.cla_backend.get_help_organisations",
            return_value=[],
        ) as mock_get_orgs,
        patch(
            "app.categories.results.views.get_fala_category_code", return_value="IMMAS"
        ),
    ):
        view = ResultPage(template="")
        result = view.get_context(category=ASYLUM_AND_IMMIGRATION)

        assert result["category_name"] == "Asylum and immigration"
        assert result["organisations"] == []
        assert result["fala_category_code"] == "IMMAS"

        mock_get_orgs.assert_not_called()


def test_get_context_with_no_category():
    with (
        patch(
            "app.categories.results.views.cla_backend.get_help_organisations",
            return_value=[],
        ) as mock_get_orgs,
        patch("app.categories.results.views.get_fala_category_code", return_value=None),
    ):
        view = ResultPage(template="")
        result = view.get_context()

        # Assertions
        assert result["category_name"] is None
        assert result["organisations"] == []
        assert result["fala_category_code"] is None

        # Verify that "other" was used as article_category_name
        mock_get_orgs.assert_called_once_with("other")


def test_get_context_with_invalid_category():
    with (
        patch(
            "app.categories.results.views.cla_backend.get_help_organisations",
            return_value=[],
        ) as mock_get_orgs,
        patch("app.categories.results.views.get_fala_category_code", return_value=None),
    ):
        view = ResultPage(template="")
        result = view.get_context(category="not_a_category_object")

        assert result["category_name"] is None
        assert result["organisations"] == []
        assert result["fala_category_code"] is None

        # Verify that "other" was used as article_category_name
        mock_get_orgs.assert_called_once_with("other")
