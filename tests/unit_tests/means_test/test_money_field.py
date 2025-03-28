from werkzeug.datastructures import MultiDict
from flask_wtf import FlaskForm
from app.means_test.validators import MoneyIntervalAmountRequired
from app.means_test.fields import MoneyIntervalField, MoneyIntervalWidget, MoneyField
import pytest


class TestIntervalForm(FlaskForm):
    money_field = MoneyIntervalField(
        widget=MoneyIntervalWidget(),
        validators=[
            MoneyIntervalAmountRequired(
                message="Please provide both amount and frequency",
                amount_message="Please provide amount",
                freq_message="Please provide frequency",
            )
        ],
        exclude_intervals=["per_4week", "per_month"],
    )


def test_money_field_valid(app, client):
    data = MultiDict([("money_field", "1000"), ("money_field", "per_week")])
    form = TestIntervalForm(formdata=data)
    assert form.validate()
    assert not form.errors


def test_money_field_both_missing(app, client):
    data = MultiDict([("money_field", ""), ("money_field", "")])
    form = TestIntervalForm(formdata=data)
    assert not form.validate()
    assert form.money_field.field_with_error == {"value", "interval"}
    assert form.errors["money_field"] == ["Please provide both amount and frequency"]


def test_money_field_only_amount_missing(app, client):
    data = MultiDict([("money_field", ""), ("money_field", "per_week")])
    form = TestIntervalForm(formdata=data)
    assert not form.validate()
    assert form.money_field.field_with_error == {"value"}
    assert form.errors["money_field"] == ["Please provide amount"]


def test_money_field_only_amount_interval(app, client):
    data = MultiDict([("money_field", "1000"), ("money_field", "")])
    form = TestIntervalForm(formdata=data)
    assert not form.validate()
    assert form.money_field.field_with_error == {"interval"}
    assert form.errors["money_field"] == ["Please provide frequency"]


def test_money_field_excluded_interval(app, client):
    data = MultiDict([("money_field", "1000"), ("money_field", "per_month")])
    form = TestIntervalForm(formdata=data)
    assert not form.validate(), "Validation should have raised an exception for invalid interval"


class TestMoneyFieldForm(FlaskForm):
    money_field = MoneyField()


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        ("£1,234.56", "1234.56"),
        ("  £ 1 2 3 4 . 5 6 ", "1234.56"),
        ("£1 234", "1234"),
    ],
)
def test_clean_input(app, client, input_value, expected_output):
    assert MoneyField.clean_input(input_value) == expected_output


@pytest.mark.parametrize(
    "input_value, expected_data",
    [
        (["£1,234.56"], 123456),
        (["0.99"], 99),
        (["0.5"], 50),
    ],
)
def test_process_formdata_valid(app, client, input_value, expected_data):
    form = TestMoneyFieldForm()
    field = form.money_field
    field.process_formdata(input_value)
    assert field.data == expected_data


@pytest.mark.parametrize(
    "input_value",
    [
        (["invalid"]),
    ],
)
def test_process_formdata_invalid_number(app, client, input_value):
    form = TestMoneyFieldForm()
    field = form.money_field
    with pytest.raises(ValueError, match="Enter a valid amount"):
        field.process_formdata(input_value)


@pytest.mark.parametrize(
    "input_value",
    [
        (["1234.567"]),
        (["1234.5601"]),
    ],
)
def test_process_formdata_too_many_decimals(app, client, input_value):
    form = TestMoneyFieldForm()
    field = form.money_field
    with pytest.raises(ValueError, match="Enter a valid amount \\(maximum 2 decimal places\\)"):
        field.process_formdata(input_value)


@pytest.mark.parametrize(
    "min_val, input_value",
    [
        (10000, ["99.99"]),
        (10000, ["-5"]),
    ],
)
def test_process_formdata_below_min(app, client, min_val, input_value):
    form = TestMoneyFieldForm()
    field = form.money_field
    field.min_val = min_val
    with pytest.raises(ValueError, match="Enter a value of more than £100.00"):
        field.process_formdata(input_value)


@pytest.mark.parametrize(
    "max_val, input_value",
    [
        (10000, ["100.01"]),
        (10000, ["£99999999"]),
    ],
)
def test_process_formdata_above_max(app, client, max_val, input_value):
    form = TestMoneyFieldForm()
    field = form.money_field
    field.max_val = max_val
    with pytest.raises(ValueError, match="Enter a value of less than £100.00"):
        field.process_formdata(input_value)


@pytest.mark.parametrize(
    "input_data, expected_value",
    [
        (123456, "1,234.56"),
    ],
)
def test_value(app, client, input_data, expected_value):
    form = TestMoneyFieldForm()
    field = form.money_field
    field.process_data(input_data)
    assert field._value() == expected_value
