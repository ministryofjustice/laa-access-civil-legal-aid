from wtforms.fields.simple import SubmitField
from app.means_test.forms import BaseMeansTestForm
from app.means_test.validators import MoneyIntervalAmountRequired, ValidateIfSession
from flask_babel import lazy_gettext as _
from app.means_test.fields import MoneyIntervalField, MoneyIntervalWidget


class ExampleForm(BaseMeansTestForm):
    template = "means_test/form-page.html"

    question = MoneyIntervalField(
        "Test money field",
        hint_text="Hint text",
        widget=MoneyIntervalWidget(),
        validators=[
            MoneyIntervalAmountRequired(
                message=_(
                    "Enter the Working Tax Credit you receive, or 0 if this doesn’t apply to you"
                ),
                freq_message=_("Tell us how often you receive Working Tax Credit"),
                amount_message=_(
                    "Tell us how much Working Tax Credit you receive"
                ),  # this is followed by the time period, e.g. "... each week"
            )
        ],
    )

    partner_question = MoneyIntervalField(
        "Test money field",
        hint_text="Hint text",
        exclude_intervals=["per_year"],
        widget=MoneyIntervalWidget(),
        validators=[
            ValidateIfSession("has_partner", True),
            MoneyIntervalAmountRequired(
                message=_(
                    "Enter the Working Tax Credit your partner receives, or 0 if it doesn’t apply"
                ),
                freq_message=_(
                    "Tell us how often your partner receives Working Tax Credit"
                ),
                amount_message=_(
                    "Tell us how much Working Tax Credit your partner receives"
                ),  # this is followed by the time period, e.g. "... each week"
            ),
        ],
    )

    submit = SubmitField("Continue")
