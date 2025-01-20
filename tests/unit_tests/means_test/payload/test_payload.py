import pytest
from app.means_test.views import MeansTest
from .test_cases import TEST_CASES


def assert_partial_dict_match(expected, actual, path=""):
    """
    Recursively check that all keys/values in expected dict exist in actual dict.
    Ignores additional keys in actual dict.
    """
    for key, expected_value in expected.items():
        current_path = f"{path}.{key}" if path else key
        assert key in actual, f"Missing key {current_path}"

        if isinstance(expected_value, dict):
            assert isinstance(actual[key], dict), f"{current_path} is not a dictionary"
            assert_partial_dict_match(expected_value, actual[key], current_path)
        else:
            assert (
                actual[key] == expected_value
            ), f"Mismatch in {current_path}. Expected {expected_value}, got {actual[key]}"


@pytest.mark.parametrize("test_case", TEST_CASES, ids=lambda t: t["id"])
def test_get_payload(test_case):
    """
    Test the get_payload method with various input scenarios.
    """
    # Get actual result
    result = MeansTest.get_payload(test_case["input"])

    # Compare expected fields with actual result
    assert_partial_dict_match(test_case["expected"], result)
