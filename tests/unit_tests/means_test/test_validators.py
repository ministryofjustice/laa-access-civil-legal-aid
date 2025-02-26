from app.means_test.validators import ValidateIf, ValidateIfType
from wtforms import StringField, SelectField, Form
from wtforms.validators import InputRequired
import pytest


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

        with pytest.raises(
            ValueError, match='No field named "non_existent_field" in form.'
        ):
            validator(form, form.field)

    @pytest.mark.parametrize(
        "test_case",
        [
            {
                "form_data": {"select_field": "test_value"},
                "dependent_field": "select_field",
                "expected_value": "test_value",
                "condition": ValidateIfType.EQ,
                "should_validate": True,
            },
            {
                "form_data": {"select_field": "different_value"},
                "dependent_field": "select_field",
                "expected_value": "test_value",
                "condition": ValidateIfType.EQ,
                "should_validate": False,
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
            assert form.validate() is False
            assert "This field is required." in form.dependent_field.errors
        else:
            assert form.validate()
            assert form.errors == {}
