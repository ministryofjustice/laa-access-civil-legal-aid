import pytest
from unittest.mock import patch
from app.find_a_legal_advisor.postcodes import get_postcode_region
from app.find_a_legal_advisor.laalaa import laalaa_search


@pytest.mark.parametrize(
    "postcode,mock_return,expected_region",
    [
        ("SW1A 1AA", {"country": "England", "nhs_ha": "London"}, "England"),
        ("JE2 3NN", {"country": "Channel Islands", "nhs_ha": "Jersey"}, "Jersey"),
        ("GY1 1WR", {"country": "Channel Islands", "nhs_ha": "Guernsey"}, "Guernsey"),
        ("INVALID", None, "Unknown"),
        (
            "AB12 3CD",
            {},  # Missing country key
            "Unknown",
        ),
        (
            "TD1 2ZZ",
            {
                "country": "  Scotland  ",
                "nhs_ha": "Borders",
            },  # Test stripping whitespace
            "Scotland",
        ),
    ],
)
def test_get_postcode_region(postcode, mock_return, expected_region):
    with patch("app.find_a_legal_advisor.postcodes.postcode_lookup") as mock_lookup:
        mock_lookup.return_value = mock_return
        result = get_postcode_region(postcode)

        assert result == expected_region

        mock_lookup.assert_called_once_with(
            postcode
        )  # Verify postcode lookup was called with the correct postcode


def test_get_postcode_region_raises_exception():
    """Test that exceptions from postcode_lookup are propagated correctly"""
    with patch("app.find_a_legal_advisor.postcodes.postcode_lookup") as mock_lookup:
        mock_lookup.side_effect = ConnectionError("API Error")

        with pytest.raises(ConnectionError):
            get_postcode_region("SW1A 1AA")


def test_laalaa_secondary_category(app):
    """Tests laalaa to ensure it returns a secondary category when required"""
    postcode = "SW1"
    category = "mhe"
    secondary_category = "com"
    page_num = 1
    categories_to_find = ["COM", "MHE"]
    with app.app_context():
        results = laalaa_search(
            postcode=postcode, categories=[category, secondary_category], page=page_num
        )
    for provider in results["results"]:
        assert any(
            category in provider["categories"] for category in categories_to_find
        ), f"None of {categories_to_find} found in provider categories: {provider['categories']}"
