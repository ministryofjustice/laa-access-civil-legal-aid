from werkzeug.datastructures import MultiDict
from flask_wtf import FlaskForm
from app.means_test.validators import MoneyIntervalAmountRequired
from app.means_test.fields import MoneyField, MoneyFieldWidget


class TestForm(FlaskForm):
    money_field = MoneyField(
        widget=MoneyFieldWidget(),
        validators=[
            MoneyIntervalAmountRequired(
                message="Please provide both amount and frequency",
                amount_message="Please provide amount",
                freq_message="Please provide frequency",
            )
        ],
        exclude_intervals=["per_year", "per_month"],
    )


def test_money_field_valid(app, client):
    data = MultiDict([("money_field", "1000"), ("money_field", "per_week")])
    form = TestForm(formdata=data)
    assert form.validate()
    assert not form.errors


def test_money_field_both_missing(app, client):
    data = MultiDict([("money_field", ""), ("money_field", "")])
    form = TestForm(formdata=data)
    assert not form.validate()
    assert form.money_field.field_with_error == ["value", "interval"]
    assert form.errors["money_field"] == ["Please provide both amount and frequency"]


def test_money_field_only_amount_missing(app, client):
    data = MultiDict([("money_field", ""), ("money_field", "per_week")])
    form = TestForm(formdata=data)
    assert not form.validate()
    assert form.money_field.field_with_error == ["value"]
    assert form.errors["money_field"] == ["Please provide amount"]


def test_money_field_only_amount_interval(app, client):
    data = MultiDict([("money_field", "1000"), ("money_field", "")])
    form = TestForm(formdata=data)
    assert not form.validate()
    assert form.money_field.field_with_error == ["interval"]
    assert form.errors["money_field"] == ["Please provide frequency"]


def test_money_field_excluded_interval(app, client):
    data = MultiDict([("money_field", "1000"), ("money_field", "per_10_year")])
    form = TestForm(formdata=data)
    try:
        form.validate()
        assert False, "Validation should have raised an exception for invalid interval"
    except ValueError:
        pass
