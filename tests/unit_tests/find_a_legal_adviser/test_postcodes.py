import pytest
from unittest.mock import patch
from app.find_a_legal_adviser.postcodes import get_postcode_region


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
    with patch("app.find_a_legal_adviser.postcodes.postcode_lookup") as mock_lookup:
        mock_lookup.return_value = mock_return
        result = get_postcode_region(postcode)

        assert result == expected_region

        mock_lookup.assert_called_once_with(postcode)  # Verify postcode lookup was called with the correct postcode


def test_get_postcode_region_raises_exception():
    """Test that exceptions from postcode_lookup are propagated correctly"""
    with patch("app.find_a_legal_adviser.postcodes.postcode_lookup") as mock_lookup:
        mock_lookup.side_effect = ConnectionError("API Error")

        with pytest.raises(ConnectionError):
            get_postcode_region("SW1A 1AA")
