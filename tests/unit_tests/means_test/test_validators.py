import pytest
from wtforms import StringField, SelectField, Form, SelectMultipleField, IntegerField
from wtforms.validators import InputRequired
from app.means_test.validators import ValidateIf, ValidateIfType, NumberRangeAllowZero


class TestValidateIf:
    def test_init(self):
        validator = ValidateIf("test_field", "test_value")
        assert validator.dependent_field_name == "test_field"
        assert validator.dependent_field_value == "test_value"
        assert validator.condition_type == ValidateIfType.EQ

    def test_field_not_found(self):
        class TestForm(Form):
            field = StringField()

        form = TestForm()
        validator = ValidateIf("non_existent_field", "test_value")

        with pytest.raises(ValueError, match='no field named "non_existent_field" in form'):
            validator(form, form.field)

    @pytest.mark.parametrize(
        "test_case",
        [
            # Case 1: Condition met, InputRequired should trigger an error
            {
                "form_data": {"select_field": "test_value"},
                "dependent_field": "select_field",
                "expected_value": "test_value",
                "condition": ValidateIfType.EQ,
                "should_validate": False,  # Expecting validation to fail (InputRequired should trigger)
            },
            # Case 2: Condition NOT met, validation should pass (no error)
            {
                "form_data": {"select_field": "different_value"},
                "dependent_field": "select_field",
                "expected_value": "test_value",
                "condition": ValidateIfType.EQ,
                "should_validate": True,  # Expecting validation to pass (ValidateIf stops validation)
            },
            # Case 3: Multi-field condition met, should trigger error
            {
                "form_data": {"multi_field": ["value1", "test_value", "value3"]},
                "dependent_field": "multi_field",
                "expected_value": "test_value",
                "condition": ValidateIfType.IN,
                "should_validate": False,  # Expecting validation to fail (InputRequired should trigger)
            },
            # Case 4: Multi-field condition NOT met, validation should pass
            {
                "form_data": {"multi_field": ["value1", "value2", "value3"]},
                "dependent_field": "multi_field",
                "expected_value": "test_value",
                "condition": ValidateIfType.IN,
                "should_validate": True,  # Expecting validation to pass (ValidateIf stops validation)
            },
        ],
    )
    def test_validation_conditions(self, test_case):
        class TestForm(Form):
            select_field = SelectField(
                choices=[
                    ("test_value", "Test Value"),
                    ("different_value", "Different Value"),
                ]
            )
            multi_field = SelectMultipleField(
                choices=[
                    ("value1", "Value 1"),
                    ("test_value", "Test Value"),
                    ("value2", "Value 2"),
                    ("value3", "Value 3"),
                ]
            )
            dependent_field = StringField(
                validators=[
                    ValidateIf(
                        test_case["dependent_field"],
                        test_case["expected_value"],
                        test_case["condition"],
                    ),
                    InputRequired("This field is required."),
                ]
            )

        form = TestForm(data=test_case["form_data"])

        if test_case["should_validate"]:
            form.validate()
            assert form.dependent_field.errors == [], f"Unexpected errors: {form.dependent_field.errors}"
        else:
            assert form.validate() is False
            assert "This field is required." in form.dependent_field.errors, (
                f"Expected error missing: {form.dependent_field.errors}"
            )


class TestNumberRange:
    def test_allows_zero(self):
        class TestForm(Form):
            amount = IntegerField("Amount", validators=[NumberRangeAllowZero(min=500)])

        form = TestForm(amount=0)
        assert form.validate()

    def test_respects_minimum(self):
        class TestForm(Form):
            amount = IntegerField("Amount", validators=[NumberRangeAllowZero(min=500)])

        form = TestForm(amount=499)
        assert form.validate() is False
        assert "Number must be at least 500." in form.amount.errors

        form = TestForm(amount=501)
        assert form.validate()

    def test_respects_maximum(self):
        class TestForm(Form):
            amount = IntegerField("Amount", validators=[NumberRangeAllowZero(min=500, max=1000)])

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

    def test_non_numeric_value(self):
        class TestForm(Form):
            amount = IntegerField("Amount", validators=[NumberRangeAllowZero(min=500)])

        form = TestForm(amount="not_a_number")
        assert form.validate() is False

    def test_none_value(self):
        class TestForm(Form):
            amount = IntegerField("Amount", validators=[NumberRangeAllowZero(min=500)])

        form = TestForm(amount=None)
        assert form.validate() is False
