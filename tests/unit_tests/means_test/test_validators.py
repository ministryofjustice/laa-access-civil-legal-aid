from wtforms import Form, IntegerField
from app.means_test.validators import NumberRangeAllowZero


def test_allows_zero():
    class TestForm(Form):
        amount = IntegerField("Amount", validators=[NumberRangeAllowZero(min=500)])

    form = TestForm(amount=0)
    assert form.validate()


def test_respects_minimum():
    class TestForm(Form):
        amount = IntegerField("Amount", validators=[NumberRangeAllowZero(min=500)])

    form = TestForm(amount=499)
    assert form.validate() is False
    assert "Number must be at least 500." in form.amount.errors

    form = TestForm(amount=501)
    assert form.validate()


def test_respects_maximum():
    class TestForm(Form):
        amount = IntegerField(
            "Amount", validators=[NumberRangeAllowZero(min=500, max=1000)]
        )

    # Test zero (should pass)
    form = TestForm(amount=0)
    assert form.validate()

    # Test value above maximum
    form = TestForm(amount=1001)
    assert form.validate() is False
    assert "Number must be between 500 and 1000." in form.amount.errors

    # Test value at maximum
    form = TestForm(amount=1000)
    assert form.validate()


def test_non_numeric_value():
    class TestForm(Form):
        amount = IntegerField("Amount", validators=[NumberRangeAllowZero(min=500)])

    form = TestForm(amount="not_a_number")
    assert form.validate() is False


def test_none_value():
    class TestForm(Form):
        amount = IntegerField("Amount", validators=[NumberRangeAllowZero(min=500)])

    form = TestForm(amount=None)
    assert form.validate() is False
