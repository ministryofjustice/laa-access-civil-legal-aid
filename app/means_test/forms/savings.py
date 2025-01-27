from wtforms.validators import InputRequired
from app.means_test.fields import MoneyField
from app.means_test.forms import BaseMeansTestForm
from app.means_test.widgets import MoneyInput
from flask_babel import lazy_gettext as _
from app.means_test.validators import ValidateIfSession


class SavingsForm(BaseMeansTestForm):
    title = _("Your savings")
    partner_title = _("You and your partner’s savings")

    template = "means_test/savings.html"

    savings = MoneyField(
        label=_("Savings"),
        widget=MoneyInput(),
        description=_(
            "The total amount of savings in cash, bank or building society; or enter 0 if you have none"
        ),
        validators=[
            InputRequired(message=_("Enter your total savings, or 0 if you have none"))
        ],
    )

    investments = MoneyField(
        label=_("Investments"),
        widget=MoneyInput(),
        description=_(
            "This includes stocks, shares, bonds (but not property); enter 0 if you have none"
        ),
        validators=[
            InputRequired(
                message=_("Enter your total investments, or 0 if you have none")
            )
        ],
    )

    valuables = MoneyField(
        label=_("Total value of items worth over £500 each"),
        widget=MoneyInput(),
        description=_("See below for examples of what valuable items to include"),
        validators=[
            ValidateIfSession("has_valuables", True),
            InputRequired(message=_("Enter the total of all valuable items over £500")),
        ],
    )

    @property
    def shown_fields(self):
        return [self.savings, self.investments, self.valuables]
