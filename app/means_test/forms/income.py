from app.means_test.fields import MoneyIntervalField, MoneyIntervalWidget
from app.means_test.forms import BaseMeansTestForm
from flask_babel import lazy_gettext as _
from flask import session
from app.means_test.validators import MoneyIntervalAmountRequired, ValidateIfSession


class SelfEmployedMoneyIntervalField(MoneyIntervalField):
    """Subclass of the MoneyIntervalField which supports alternate hint_text depending on if the user is self-employed"""

    def __init__(self, *args, self_employed_hint_text=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.self_employed_hint_text = self_employed_hint_text
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
        return self.self_employed_hint_text.get(self.get_employment_status(), None)

    @hint_text.setter
    def hint_text(self, value):
        self._hint_text = value


class IncomeForm(BaseMeansTestForm):
    @property
    def page_title(self):
        has_partner = session.get_eligibility().has_partner
        employed = session.get_eligibility().is_employed or session.get_eligibility().is_self_employed
        if has_partner:
            if employed:
                return _("You and your partner’s income and tax")
            return _("You and your partner’s money coming in")
        elif employed:
            return _("Your income and tax")
        return _("Your money coming in")

    template = "means_test/income.html"

    @classmethod
    def should_show(cls) -> bool:
        return not session.get("eligibility").has_passported_benefits

    earnings = SelfEmployedMoneyIntervalField(
        _("Wages before tax"),
        self_employed_hint_text={
            "employed": _("For example, £32.18 per week"),
            "self_employed": _("This includes any earnings from self-employment"),
            "both": _("This includes all wages and any earnings from self-employment"),
        },
        widget=MoneyIntervalWidget(),
        validators=[
            ValidateIfSession("is_employed_or_self_employed", True),
            MoneyIntervalAmountRequired(
                message=_("Tell us how much you receive in wages"),
                freq_message=_("Tell us how often you receive wages"),
                amount_message=_("Tell us how much you receive in wages"),
            ),
        ],
        exclude_intervals=["per_2week"],
    )

    income_tax = SelfEmployedMoneyIntervalField(
        label=_("Income tax"),
        self_employed_hint_text={
            "employed": _("Tax paid directly out of wages"),
            "self_employed": _("Any tax paid on self-employed earnings"),
            "both": _("Tax paid directly out of wages and any tax paid on self-employed earnings"),
        },
        widget=MoneyIntervalWidget(),
        validators=[
            ValidateIfSession("is_employed_or_self_employed", True),
            MoneyIntervalAmountRequired(
                message=_("Tell us how much income tax you pay"),
                freq_message=_("Tell us how often you pay income tax"),
                amount_message=_("Tell us how much income tax you pay"),
            ),
        ],
        exclude_intervals=["per_2week"],
    )

    national_insurance = SelfEmployedMoneyIntervalField(
        _("National Insurance contributions"),
        self_employed_hint_text={
            "employed": _("Check the payslip"),
            "self_employed": _("Check the National Insurance statement"),
            "both": _("Check the payslip or National Insurance statement if self-employed"),
        },
        widget=MoneyIntervalWidget(),
        validators=[
            ValidateIfSession("is_employed_or_self_employed", True),
            MoneyIntervalAmountRequired(
                message=_("Tell us how much National Insurance you pay"),
                freq_message=_("Tell us how often you pay National Insurance"),
                amount_message=_("Tell us how much National Insurance you pay"),
            ),
        ],
        exclude_intervals=["per_2week"],
    )

    working_tax_credit = MoneyIntervalField(
        _("Working Tax Credit"),
        hint_text=_("Extra money for people who work and have a low income, enter 0 if this doesn't apply to you"),
        widget=MoneyIntervalWidget(),
        validators=[
            ValidateIfSession("is_employed_or_self_employed", True),
            MoneyIntervalAmountRequired(
                message=_("Enter the Working Tax Credit you receive, or 0 if this doesn't apply to you"),
                freq_message=_("Tell us how often you receive Working Tax Credit"),
                amount_message=_("Tell us how much Working Tax Credit you receive"),
            ),
        ],
        exclude_intervals=["per_2week"],
    )

    child_tax_credit = MoneyIntervalField(
        _("Child Tax Credit"),
        hint_text=_("The total amount you get for all your children, enter 0 if this doesn't apply to you"),
        widget=MoneyIntervalWidget(),
        validators=[
            ValidateIfSession("is_employed_or_self_employed", True),
            MoneyIntervalAmountRequired(
                message=_("Enter the Child Tax Credit you receive, or 0 if this doesn't apply to you"),
                freq_message=_("Tell us how often you receive Child Tax Credit"),
                amount_message=_("Tell us how much Child Tax Credit you receive"),
            ),
        ],
        exclude_intervals=["per_2week"],
    )

    maintenance_received = MoneyIntervalField(
        _("Maintenance received"),
        hint_text=_("Payments you get from an ex-partner, or enter 0 if this doesn't apply to you"),
        widget=MoneyIntervalWidget(),
        validators=[
            MoneyIntervalAmountRequired(
                message=_("Enter the total amount of maintenance you receive, or 0 if this doesn't apply to you"),
                freq_message=_("Tell us how often you receive maintenance"),
                amount_message=_("Tell us how much maintenance you receive"),
            )
        ],
        exclude_intervals=["per_2week"],
    )

    pension = MoneyIntervalField(
        _("Pension received"),
        hint_text=_("Payments you receive if you're retired, enter 0 if this doesn't apply to you"),
        widget=MoneyIntervalWidget(),
        validators=[
            MoneyIntervalAmountRequired(
                message=_("Enter the pension you receive, or 0 if this doesn't apply to you"),
                freq_message=_("Tell us how often you receive your pension"),
                amount_message=_("Tell us how much pension you receive"),
            )
        ],
        exclude_intervals=["per_2week"],
    )

    other_income = MoneyIntervalField(
        _("Any other income"),
        hint_text=_(
            "For example, student grants, income from trust funds, dividends, or enter 0 if this doesn't apply to you"
        ),
        widget=MoneyIntervalWidget(),
        validators=[
            MoneyIntervalAmountRequired(
                message=_("Enter the total amount of other income you receive, or 0 if this doesn't apply to you"),
                freq_message=_("Tell us how often you receive this other income"),
                amount_message=_("Tell us how much other income you receive"),
            )
        ],
        exclude_intervals=["per_2week"],
    )

    # Partner-specific fields
    partner_earnings = SelfEmployedMoneyIntervalField(
        _("Wages before tax"),
        self_employed_hint_text={
            "employed": _("For example, £32.18 per week"),
            "self_employed": _("This includes any earnings from self-employment"),
            "both": _("This includes all wages and any earnings from self-employment"),
        },
        widget=MoneyIntervalWidget(),
        validators=[
            ValidateIfSession("has_partner", True),
            ValidateIfSession("is_partner_employed", True),
            MoneyIntervalAmountRequired(
                message=_("Tell us how much your partner receives in wages"),
                freq_message=_("Tell us how often your partner receives wages"),
                amount_message=_("Tell us how much your partner receives in wages"),
            ),
        ],
        exclude_intervals=["per_2week"],
    )

    partner_income_tax = SelfEmployedMoneyIntervalField(
        label=_("Income tax"),
        self_employed_hint_text={
            "employed": _("Tax paid directly out of wages"),
            "self_employed": _("Any tax paid on self-employed earnings"),
            "both": _("Tax paid directly out of wages and any tax paid on self-employed earnings"),
        },
        widget=MoneyIntervalWidget(),
        validators=[
            ValidateIfSession("has_partner", True),
            ValidateIfSession("is_partner_employed", True),
            MoneyIntervalAmountRequired(
                message=_("Tell us how much income tax your partner pays"),
                freq_message=_("Tell us how often your partner pays income tax"),
                amount_message=_("Tell us how much income tax your partner pays"),
            ),
        ],
        exclude_intervals=["per_2week"],
    )

    partner_national_insurance = SelfEmployedMoneyIntervalField(
        _("National Insurance contributions"),
        self_employed_hint_text={
            "employed": _("Check the payslip"),
            "self_employed": _("Check the National Insurance statement"),
            "both": _("Check the payslip or National Insurance statement if self-employed"),
        },
        widget=MoneyIntervalWidget(),
        validators=[
            ValidateIfSession("has_partner", True),
            ValidateIfSession("is_partner_employed", True),
            MoneyIntervalAmountRequired(
                message=_("Tell us how much National Insurance your partner pays"),
                freq_message=_("Tell us how often your partner pays National Insurance"),
                amount_message=_("Tell us how much National Insurance your partner pays"),
            ),
        ],
        exclude_intervals=["per_2week"],
    )

    partner_working_tax_credit = MoneyIntervalField(
        _("Working Tax Credit"),
        hint_text=_(
            "Extra money for people who work and have a low income, enter 0 if this doesn't apply to your partner"
        ),
        widget=MoneyIntervalWidget(),
        validators=[
            ValidateIfSession("has_partner", True),
            ValidateIfSession("is_partner_employed", True),
            MoneyIntervalAmountRequired(
                message=_("Enter the Working Tax Credit your partner receives, or 0 if it doesn't apply"),
                freq_message=_("Tell us how often your partner receives Working Tax Credit"),
                amount_message=_("Tell us how much Working Tax Credit your partner receives"),
            ),
        ],
    )

    partner_maintenance_received = MoneyIntervalField(
        _("Maintenance received"),
        hint_text=_("Payments your partner gets from an ex-partner, or enter 0 if this doesn't apply to your partner"),
        widget=MoneyIntervalWidget(),
        validators=[
            ValidateIfSession("has_partner", True),
            MoneyIntervalAmountRequired(
                message=_("Enter the total amount of maintenance your partner receives, or 0 if this doesn't apply"),
                freq_message=_("Tell us how often your partner receives maintenance"),
                amount_message=_("Tell us how much maintenance your partner receives"),
            ),
        ],
        exclude_intervals=["per_2week"],
    )

    partner_pension = MoneyIntervalField(
        _("Pension received"),
        hint_text=_("Payments your partner receives if they're retired, enter 0 if this doesn't apply to your partner"),
        widget=MoneyIntervalWidget(),
        validators=[
            ValidateIfSession("has_partner", True),
            MoneyIntervalAmountRequired(
                message=_("Enter the pension your partner receives, or 0 if this doesn't apply"),
                freq_message=_("Tell us how often your partner receives their pension"),
                amount_message=_("Tell us how much pension your partner receives"),
            ),
        ],
        exclude_intervals=["per_2week"],
    )

    partner_other_income = MoneyIntervalField(
        _("Any other income"),
        hint_text=_(
            "For example, student grants, income from trust funds, dividends, or enter 0 if this doesn't apply to your partner"
        ),
        widget=MoneyIntervalWidget(),
        validators=[
            ValidateIfSession("has_partner", True),
            MoneyIntervalAmountRequired(
                message=_("Enter the other income your partner receives, or 0 if this doesn't apply"),
                freq_message=_("Tell us how often your partner receives this other income"),
                amount_message=_("Tell us how much other income your partner receives"),
            ),
        ],
        exclude_intervals=["per_2week"],
    )

    @property
    def shown_fields(self):
        fields = {"self": [], "partner": []}
        if session.get_eligibility().is_employed or session.get_eligibility().is_self_employed:
            fields["self"].extend(
                [
                    self.earnings,
                    self.income_tax,
                    self.national_insurance,
                    self.working_tax_credit,
                    self.child_tax_credit,
                ]
            )

        fields["self"].extend([self.maintenance_received, self.pension, self.other_income])

        if session.get_eligibility().has_partner:
            if session.get_eligibility().is_partner_employed or session.get_eligibility().is_partner_self_employed:
                fields["partner"].extend(
                    [
                        self.partner_earnings,
                        self.partner_income_tax,
                        self.partner_national_insurance,
                        self.partner_working_tax_credit,
                    ]
                )
            fields["partner"].extend(
                [
                    self.partner_maintenance_received,
                    self.partner_pension,
                    self.partner_other_income,
                ]
            )

        return fields
