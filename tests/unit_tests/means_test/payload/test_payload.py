from unittest.mock import patch
import pytest
from app.session import Session
from app.categories.constants import get_category_from_code
from app.means_test.payload import MeansTestPayload
from .test_cases import (
    ABOUT_YOU_TEST_CASES,
    INCOME_TEST_CASES,
    SAVINGS_TEST_CASES,
    OUTGOINGS_TEST_CASES,
    PROPERTIES_TEST_CASES,
)


def assert_partial_dict_match(expected: dict, actual: dict, path: str = "") -> None:
    """
    Recursively check that all keys/values in expected dict exist in actual dict.

    Args:
        expected: Dictionary containing expected key/value pairs
        actual: Dictionary to check against
        path: Current path in the nested structure for error reporting

    Raises:
        AssertionError: If expected keys/values don't match actual
    """
    for key, expected_value in expected.items():
        current_path = f"{path}.{key}" if path else key
        assert key in actual, f"Missing key {current_path}"

        if isinstance(expected_value, dict):
            assert isinstance(actual[key], dict), f"{current_path} is not a dictionary"
            assert_partial_dict_match(expected_value, actual[key], current_path)
        else:
            assert actual[key] == expected_value, (
                f"Mismatch in {current_path}. Expected {expected_value}, got {actual[key]}"
            )


@pytest.mark.parametrize(
    "test_case",
    ABOUT_YOU_TEST_CASES + INCOME_TEST_CASES + SAVINGS_TEST_CASES + OUTGOINGS_TEST_CASES + PROPERTIES_TEST_CASES,
    ids=lambda t: t["id"],
)
def test_get_means_test_payload(test_case: dict, app, client) -> None:
    """
    Test the get_payload method with various input scenarios.

    Args:
        test_case: Dictionary containing test input and expected output
    """
    mock_session = Session()
    for form in test_case["input"].forms:
        mock_session.get_eligibility().forms[form] = test_case["input"].forms[form]
    mock_session.category = get_category_from_code(test_case["input"].category)

    with patch("app.means_test.payload.session", mock_session):
        payload = MeansTestPayload()
        payload.update_from_session()
        assert_partial_dict_match(test_case["expected"], payload)
