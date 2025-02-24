from wtforms import Form, IntegerField
from wtforms.validators import NumberRange
from app.means_test.validators import AllowedExceptions


def test_single_allowed_value():
    class TestForm(Form):
        amount = IntegerField(
            "Amount", validators=[AllowedExceptions(0), NumberRange(min=501)]
        )

    form = TestForm(amount=0)
    assert form.validate()


def test_list_of_allowed_values():
    class TestForm(Form):
        amount = IntegerField(
            "Amount", validators=[AllowedExceptions([0, 1, 2]), NumberRange(min=501)]
        )

    # Test each allowed value
    for value in [0, 1, 2]:
        form = TestForm(amount=value)
        assert form.validate()


def test_non_allowed_value():
    class TestForm(Form):
        amount = IntegerField(
            "Amount", validators=[AllowedExceptions([0, 1]), NumberRange(min=500)]
        )

    # Should fail because 3 is neither in allowed values nor >= 500
    form = TestForm(amount=3)
    assert form.validate() is False
    assert "Number must be at least 500." in form.amount.errors

    # Should pass because 500 meets the NumberRange requirement
    form = TestForm(amount=500)
    assert form.validate()
