from wtforms.fields import IntegerField, RadioField, SelectMultipleField
from app.means_test.forms import BaseMeansTestForm
from app.means_test.fields import MoneyIntervalField


class TestForm(BaseMeansTestForm):
    confirm = RadioField("Do you like colours", choices=[("yes", "Yes"), ("no", "No")])
    age = IntegerField("Please enter your age")
    colour = SelectMultipleField(
        label="Please select your favourite colour",
        choices=[("red", "Red"), ("green", "Green"), ("blue", "Blue")],
    )
    salary = MoneyIntervalField("What is your salary?")

    def filter_summary(self, summary: dict) -> dict:
        confirm = summary.get("confirm", "no")
        if "colour" in summary and confirm == "no":
            del summary["colour"]
        return summary


def test_summary(app):
    expected_summary = {
        "confirm": {
            "question": "Do you like colours",
            "answer": "Yes",
            "id": "confirm",
        },
        "age": {
            "question": "Please enter your age",
            "answer": 20,
            "id": "age",
        },
        "colour": {
            "question": "Please select your favourite colour",
            "answer": ["Red"],
            "id": "colour",
        },
        "salary": {
            "question": "What is your salary?",
            "answer": "£200.50 (4 weekly)",
            "id": "salary",
        },
    }

    with app.app_context():
        salary = {"per_interval_value": 20050, "interval_period": "per_4week"}
        form = TestForm(
            **{"confirm": "yes", "age": 20, "colour": ["red"], "salary": salary}
        )
        summary = form.summary()
        assert summary == expected_summary


def test_summary_with_multiple(app):
    expected_summary = {
        "confirm": {
            "question": "Do you like colours",
            "answer": "Yes",
            "id": "confirm",
        },
        "colour": {
            "question": "Please select your favourite colour",
            "answer": ["Red", "Blue"],
            "id": "colour",
        },
    }

    with app.app_context():
        form = TestForm(**{"confirm": "yes", "colour": ["red", "blue"]})
        summary = form.summary()
        assert summary == expected_summary
