from wtforms import Form, SelectMultipleField
import pytest
from app.categories.validators import ExclusiveValue


class TestForm(Form):
    choices = SelectMultipleField(
        "Test Field",
        choices=[("a", "Option A"), ("b", "Option B"), ("none", "None of these")],
        validators=[ExclusiveValue()],
    )


@pytest.fixture
def form():
    return TestForm()


def test_single_none_selection_valid(app, form):
    with app.app_context():
        form.choices.data = ["none"]
        assert form.validate() is True
        assert not form.errors


def test_multiple_selections_without_none_valid(app, form):
    with app.app_context():
        form.choices.data = ["a", "b"]
        assert form.validate() is True
        assert not form.errors


def test_none_with_other_selections_invalid(app, form):
    with app.app_context():
        form.choices.data = ["a", "none"]
        assert form.validate() is False
        assert form.errors["choices"][0] == "Invalid choice"


def test_empty_selection_valid(app, form):
    with app.app_context():
        form.choices.data = []
        assert form.validate() is True
        assert not form.errors


def test_custom_exclusive_value(app):
    class CustomExclusiveForm(Form):
        choices = SelectMultipleField(
            "Test Field",
            choices=[("a", "A"), ("b", "B"), ("c", "C")],
            validators=[ExclusiveValue(exclusive_value="a")],
        )

    with app.app_context():
        form = CustomExclusiveForm()
        form.choices.data = ["a", "b"]
        assert form.validate() is False
        assert form.errors["choices"][0] == "Invalid choice"


def test_field_not_submitted(app, form):
    with app.app_context():
        form.choices.data = None
        assert form.validate() is True
        assert not form.errors
