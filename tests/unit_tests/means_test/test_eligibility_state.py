import pytest
from app.means_test.api import EligibilityState


class TestEligibilityState:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("YES", EligibilityState.YES),
            ("yEs", EligibilityState.YES),
            ("NO", EligibilityState.NO),
            ("nO", EligibilityState.NO),
            ("UNKNOWN", EligibilityState.UNKNOWN),
            ("unKNOWN", EligibilityState.UNKNOWN),
        ],
    )
    def test_case_insensitivity(value, expected):
        assert EligibilityState(value) == expected

    @pytest.mark.parametrize(
        "value, expected",
        [
            ("invalid", EligibilityState.UNKNOWN),
            ("maybe", EligibilityState.UNKNOWN),
            ("", EligibilityState.UNKNOWN),
        ],
    )
    def test_invalid_values(value, expected):
        assert EligibilityState(value) == expected

    @pytest.mark.parametrize("value", [123, None, True])
    def test_non_string_values(value):
        assert EligibilityState._missing_(value) is None

    @pytest.mark.parametrize(
        "value, expected",
        [
            (EligibilityState.YES, True),
            (EligibilityState.NO, False),
            (EligibilityState.UNKNOWN, False),
        ],
    )
    def test_bool_conversion(value, expected):
        if value:
            assert expected
        else:
            assert not expected
