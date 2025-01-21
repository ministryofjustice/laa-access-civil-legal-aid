from app.means_test.fields import MoneyIntervalField, MoneyIntervalFieldWidget
from app.means_test.forms import BaseMeansTestForm
from flask_babel import lazy_gettext as _
from flask import session
from app.means_test.validators import MoneyIntervalAmountRequired


class SelfEmployedMoneyIntervalField(MoneyIntervalField):
    """Subclass of the MoneyIntervalField which supports alternate hint_text depending on if the user is self-employed"""

    def __init__(self, *args, self_employed_descriptions=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.self_employed_descriptions = self_employed_descriptions
        self._hint_text = ""

    @staticmethod
    def get_employment_status():
        is_employed = session.get_eligibility().is_employed
        is_self_employed = session.get_eligibility().is_self_employed
        if is_employed and is_self_employed:
            return "both"
        if is_self_employed:
            return "self_employed"
        if is_employed:
            return "employed"
        return "neither"

    @property
    def hint_text(self):
        return self.self_employed_descriptions.get(self.get_employment_status(), None)

    @hint_text.setter
    def hint_text(self, value):
        self._hint_text = value


class IncomeForm(BaseMeansTestForm):
    title = _("Your money coming in")

    template = "means_test/income.html"

    earnings = SelfEmployedMoneyIntervalField(
        _("Wages before tax"),
        self_employed_descriptions={
            "self_employed": _("This includes any earnings from self-employment"),
            "both": _("This includes all wages and any earnings from self-employment"),
        },
        widget=MoneyIntervalFieldWidget(),
        validators=[
            MoneyIntervalAmountRequired(
                message=_("Tell us how much you receive in wages"),
                freq_message=_("Tell us how often you receive wages"),
                amount_message=_(
                    "Tell us how much you receive in wages"
                ),  # this is followed by the time period, e.g. "... each week"
                partner_message=_("Tell us how much your partner receives in wages"),
                partner_freq_message=_("Tell us how often your partner receives wages"),
                partner_amount_message=_(
                    "Tell us how much your partner receives in wages"
                ),  # this is followed by the time period, e.g. "... each week"
            )
        ],
    )
    income_tax = SelfEmployedMoneyIntervalField(
        label=_("Income tax"),
        self_employed_descriptions={
            "employed": _("Tax paid directly out of wages"),
            "self_employed": _("Any tax paid on self-employed earnings"),
            "both": _(
                "Tax paid directly out of wages and any tax paid on self-employed earnings"
            ),
        },
        widget=MoneyIntervalFieldWidget(),
        validators=[
            MoneyIntervalAmountRequired(
                message=_("Tell us how much income tax you pay"),
                freq_message=_("Tell us how often you pay income tax"),
                amount_message=_(
                    "Tell us how much income tax you pay"
                ),  # this is followed by the time period, e.g. "... each week"
                partner_message=_("Tell us how much income tax your partner pays"),
                partner_freq_message=_(
                    "Tell us how often your partner pays income tax"
                ),
                partner_amount_message=_(
                    "Tell us how much income tax your partner pays"
                ),  # this is followed by the time period, e.g. "... each week"
            )
        ],
    )
    national_insurance = SelfEmployedMoneyIntervalField(
        _("National Insurance contributions"),
        self_employed_descriptions={
            "employed": _("Check the payslip"),
            "self_employed": _("Check the National Insurance statement"),
            "both": _(
                "Check the payslip or National Insurance statement if self-employed"
            ),
        },
        widget=MoneyIntervalFieldWidget(),
        validators=[
            MoneyIntervalAmountRequired(
                message=_("Tell us how much National Insurance you pay"),
                freq_message=_("Tell us how often you pay National Insurance"),
                amount_message=_(
                    "Tell us how much National Insurance you pay"
                ),  # this is followed by the time period, e.g. "... each week"
                partner_message=_(
                    "Tell us how much National Insurance your partner pays"
                ),
                partner_freq_message=_(
                    "Tell us how often your partner pays National Insurance"
                ),
                partner_amount_message=_(
                    "Tell us how much National Insurance your partner pays"
                ),  # this is followed by the time period, e.g. "... each week"
            )
        ],
    )
    working_tax_credit = MoneyIntervalField(
        _("Working Tax Credit"),
        hint_text=_(
            "Extra money for people who work and have a low income, enter 0 if this doesn’t apply to you"
        ),
        widget=MoneyIntervalFieldWidget(),
        validators=[
            MoneyIntervalAmountRequired(
                message=_(
                    "Enter the Working Tax Credit you receive, or 0 if this doesn’t apply to you"
                ),
                freq_message=_("Tell us how often you receive Working Tax Credit"),
                amount_message=_(
                    "Tell us how much Working Tax Credit you receive"
                ),  # this is followed by the time period, e.g. "... each week"
                partner_message=_(
                    "Enter the Working Tax Credit your partner receives, or 0 if it doesn’t apply"
                ),
                partner_freq_message=_(
                    "Tell us how often your partner receives Working Tax Credit"
                ),
                partner_amount_message=_(
                    "Tell us how much Working Tax Credit your partner receives"
                ),  # this is followed by the time period, e.g. "... each week"
            )
        ],
    )
    child_tax_credit = MoneyIntervalField(
        _("Child Tax Credit"),
        hint_text=_(
            "The total amount you get for all your children, enter 0 if this doesn’t apply to you"
        ),
        widget=MoneyIntervalFieldWidget(),
        validators=[
            MoneyIntervalAmountRequired(
                message=_(
                    "Enter the Child Tax Credit you receive, or 0 if this doesn’t apply to you"
                ),
                freq_message=_("Tell us how often you receive Child Tax Credit"),
                amount_message=_(
                    "Tell us how much Child Tax Credit you receive"
                ),  # this is followed by the time period, e.g. "... each week"
                partner_message=_(
                    "Enter the Child Tax Credit your partner receives, or 0 if it doesn’t apply"
                ),
                partner_freq_message=_(
                    "Tell us how often your partner receive Child Tax Credit"
                ),
                partner_amount_message=_(
                    "Tell us how much Child Tax Credit your partner receives"
                ),  # this is followed by the time period, e.g. "... each week"
            )
        ],
    )
    maintenance = MoneyIntervalField(
        _("Maintenance received"),
        description=_(
            "Payments you get from an ex-partner, or enter 0 if this doesn’t apply to you"
        ),
        widget=MoneyIntervalFieldWidget(),
        validators=[
            MoneyIntervalAmountRequired(
                message=_(
                    "Enter the total amount of maintenance you receive, or 0 if this doesn’t apply to you"
                ),
                freq_message=_("Tell us how often you receive maintenance"),
                amount_message=_(
                    "Tell us how much maintenance you receive"
                ),  # this is followed by the time period, e.g. "... each week"
                partner_message=_(
                    "Enter the total amount of maintenance your partner receives, or 0 if this doesn’t apply"
                ),
                partner_freq_message=_(
                    "Tell us how often your partner receives maintenance"
                ),
                partner_amount_message=_(
                    "Tell us how much maintenance your partner receives"
                ),  # this is followed by the time period, e.g. "... each week"
            )
        ],
    )
    pension = MoneyIntervalField(
        _("Pension received"),
        description=_(
            "Payments you receive if you’re retired, enter 0 if this doesn’t apply to you"
        ),
        widget=MoneyIntervalFieldWidget(),
        validators=[
            MoneyIntervalAmountRequired(
                message=_(
                    "Enter the pension you receive, or 0 if this doesn’t apply to you"
                ),
                freq_message=_("Tell us how often you receive your pension"),
                amount_message=_(
                    "Tell us how much pension you receive"
                ),  # this is followed by the time period, e.g. "... each week"
                partner_message=_(
                    "Enter the pension your partner receives, or 0 if this doesn’t apply"
                ),
                partner_freq_message=_(
                    "Tell us how often your partner receives their pension"
                ),
                partner_amount_message=_(
                    "Tell us how much pension your partner receives"
                ),  # this is followed by the time period, e.g. "... each week"
            )
        ],
    )
    other_income = MoneyIntervalField(
        _("Any other income"),
        description=_(
            "For example, student grants, income from trust funds, dividends, or enter 0 if this doesn’t apply to you"
        ),
        widget=MoneyIntervalFieldWidget(),
        validators=[
            MoneyIntervalAmountRequired(
                message=_(
                    "Enter the total amount of other income you receive, or 0 if this doesn’t apply to you"
                ),
                freq_message=_("Tell us how often you receive this other income"),
                amount_message=_(
                    "Tell us how much other income you receive"
                ),  # this is followed by the time period, e.g. "... each week"
                partner_message=_(
                    "Enter the other income your partner receives, or 0 if this doesn’t apply"
                ),
                partner_freq_message=_(
                    "Tell us how often your partner receives this other income"
                ),
                partner_amount_message=_(
                    "Tell us how much other income your partner receives"
                ),  # this is followed by the time period, e.g. "... each week"
            )
        ],
    )
