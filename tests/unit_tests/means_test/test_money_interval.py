from app.means_test.money_interval import MoneyInterval


def test_money_interval():
    instance = MoneyInterval(["100", "per_week"])
    assert instance.amount == 10000
    assert instance.amount_to_pounds() == 100

    factor = 52.0 / 12.0
    expected_monthly_amount = 10000 * factor
    assert instance.per_month()["per_interval_value"] == int(expected_monthly_amount)


def test_money_interval_with_pence():
    instance = MoneyInterval(["25.50", "per_week"])
    assert instance.amount == 2550
    assert instance.amount_to_pounds() == 25.50


def test_money_interval_addition_per_week():
    """Add  per week and per month intervals"""
    first_amount_pounds = 100
    first_amount_pence = 10000
    second_amount_pounds = 200
    second_amount_pence = 20000
    instance = MoneyInterval([str(first_amount_pounds), "per_week"]) + {
        "per_interval_value": str(second_amount_pounds),
        "interval_period": "per_month",
    }
    factor = 52.0 / 12.0
    expected_monthly_amount = (
        int(int(first_amount_pence) * factor) + second_amount_pence
    )
    assert instance.amount == expected_monthly_amount


def test_money_interval_addition_per_month():
    """Add two per month intervals"""
    first_amount_pounds = 100
    first_amount_pence = 10000
    second_amount_pounds = 200
    second_amount_pence = 20000
    instance = MoneyInterval([str(first_amount_pounds), "per_month"]) + {
        "per_interval_value": str(second_amount_pounds),
        "interval_period": "per_month",
    }
    factor = 1.0
    expected_monthly_amount = int(first_amount_pence * factor) + second_amount_pence
    assert instance.amount == expected_monthly_amount


def test_money_interval_incorrect_field():
    instance = MoneyInterval(["test", "per_week"])
    assert instance.amount is None

    assert instance.per_month()["per_interval_value"] == 0
