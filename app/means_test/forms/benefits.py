from flask import session
from flask_babel import lazy_gettext as _
from wtforms.validators import InputRequired
from app.means_test.widgets import MeansTestCheckboxInput, MeansTestRadioInput
from app.means_test.forms import BaseMeansTestForm
from app.means_test.fields import MoneyIntervalField, MoneyIntervalWidget
from app.means_test.partner_fields import PartnerMultiCheckboxField, PartnerYesNoField
from app.means_test.validators import (
    MoneyIntervalAmountRequired,
    ValidateIfSession,
    ValidateIf,
    ValidateIfType,
)
from dataclasses import dataclass, field


@dataclass
class BenefitsData:
    BENEFITS_CHOICES = [
        ("child_benefit", _("Child Benefit")),
        ("pension_credit", _("Guarantee Credit")),
        ("income_support", _("Income Support")),
        ("job_seekers_allowance", _("Income-based Jobseeker's Allowance")),
        ("employment_support", _("Income-related Employment and Support Allowance")),
        ("universal_credit", _("Universal Credit")),
        ("other-benefit", _("Any other benefits")),
    ]
    benefits: list = field(default_factory=list)
    child_benefits: dict = field(default_factory=dict)

    @property
    def passported_benefits(self):
        others = ["child_benefit", "other-benefit"]
        return [name for name, label in self.BENEFITS_CHOICES if name not in others]

    @property
    def specific_benefits(self):
        return {
            "pension_credit": "pension_credit" in self.benefits,
            "job_seekers_allowance": "job_seekers_allowance" in self.benefits,
            "employment_support": "employment_support" in self.benefits,
            "universal_credit": "universal_credit" in self.benefits,
            "income_support": "income_support" in self.benefits,
        }

    @property
    def is_passported(self) -> bool:
        return bool(set(self.benefits).intersection(self.passported_benefits))


@dataclass
class AdditionalBenefitData:
    benefits: list = field(default_factory=list)
    other_benefits: list = field(default_factory=list)
    total_other_benefit: dict = field(default_factory=dict)


def get_benefits_choices():
    choices = BenefitsData.BENEFITS_CHOICES.copy()
    # Add the OR text in
    choices.insert(-1, ("", ""))
    return choices


class BenefitsForm(BaseMeansTestForm):
    title = _("Which benefits do you receive?")
    partner_title = _("Which benefits do you and your partner receive?")

    template = "means_test/benefits.html"

    benefits = PartnerMultiCheckboxField(
        label=title,
        partner_label=partner_title,
        widget=MeansTestCheckboxInput(
            is_inline=False,
            show_divider=True,
            hint_text=_("Select all that apply"),
            heading_class="govuk-fieldset__legend--xl",
        ),
        choices=get_benefits_choices(),
    )

    child_benefits = MoneyIntervalField(
        _("If yes, enter the total amount you get for all your children"),
        hint_text=_("For example, £32.18 per week"),
        exclude_intervals=["per_month"],
        widget=MoneyIntervalWidget(),
        validators=[
            ValidateIfSession("is_eligible_for_child_benefits", True),
            ValidateIf("benefits", "child_benefit", ValidateIfType.IN),
            MoneyIntervalAmountRequired(
                message=_("Enter the Child Benefit you receive"),
                freq_message=_("Tell us how often you receive Child Benefit"),
                amount_message=_("Tell us how much Child Benefit you receive each"),
            ),
        ],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove child-benefit option if they don't have any children or dependants
        eligibility = session.get_eligibility()
        if not eligibility.is_eligible_for_child_benefits:
            self.benefits.choices = list(filter(lambda benefit: benefit[0] != "child_benefit", self.benefits.choices))

    @property
    def data(self):
        # Only return data for our fields and not including the core fields
        data = super().data
        return {key: value for key, value in data.items() if key not in ["csrf_token", "submit"]}

    @classmethod
    def should_show(cls) -> bool:
        return session.get_eligibility().on_benefits


class AdditionalBenefitsForm(BaseMeansTestForm):
    title = _("Your additional benefits")
    partner_title = _("You and your partner’s additional benefits")
    description = _(
        "You’ll need to provide evidence of the financial information you’ve given us through this service."
    )
    template = "means_test/additional-benefits.html"
    benefits = PartnerMultiCheckboxField(
        label=_("Do you get any of these benefits?"),
        partner_label=_("Do you or your partner get any of these benefits?"),
        widget=MeansTestCheckboxInput(
            is_inline=False,
            show_divider=False,
            hint_text=_("These benefits don’t count as income. Please tick the ones you receive."),
        ),
        choices=[
            ("armed-forces-independance", _("Armed Forces Independence payment")),
            ("attendance", _("Attendance Allowance")),
            ("back-to-work-bonus", _("Back to Work Bonus")),
            ("care-community", _("Care in the community Direct Payment")),
            ("carers", _("Carers’ Allowance")),
            ("constant-attendance", _("Constant Attendance Allowance")),
            ("ctax-benefits", _("Council Tax Benefits")),
            ("disability-living", _("Disability Living Allowance")),
            ("ex-severe-disablement", _("Exceptionally Severe Disablement Allowance")),
            ("fostering", _("Fostering Allowance")),
            ("housing", _("Housing Benefit")),
            ("indep-living", _("Independent Living Funds payment")),
            ("personal-indep", _("Personal Independence Payments")),
            ("severe-disablement", _("Severe Disablement Allowance")),
            ("social-fund", _("Social Fund Payments")),
            ("special-ed-needs", _("Special Education Needs (SEN) direct payment")),
            ("war-pension", _("War Pension")),
        ],
    )

    other_benefits = PartnerYesNoField(
        label=_("Do you receive any other benefits not listed above? "),
        partner_label=_("Do you or your partner receive any other benefits not listed above? "),
        description=_(
            "For example, National Asylum Support Service Benefit, "
            "Incapacity Benefit, Contribution-based Jobseeker’s "
            "Allowance"
        ),
        widget=MeansTestRadioInput(),
        validators=[InputRequired(message=_("Tell us whether you receive any other benefits"))],
    )
    total_other_benefit = MoneyIntervalField(
        label=_("If Yes, total amount of benefits not listed above"),
        hint_text=_("For example, £32.18 per week"),
        exclude_intervals=["per_month"],
        widget=MoneyIntervalWidget(),
        validators=[
            ValidateIf("other_benefits", True),
            MoneyIntervalAmountRequired(
                message=_("Tell us how much you receive in other benefits"),
                freq_message=_("Tell us how often you receive these other benefits"),
                amount_message=_("Tell us how much you receive in other benefits"),
            ),
        ],
    )

    @property
    def data(self):
        # Only return data for our fields and not including the core fields
        data = super().data
        return {key: value for key, value in data.items() if key not in ["csrf_token", "submit"]}

    @classmethod
    def should_show(cls) -> bool:
        data = session.get("eligibility").forms.get("benefits")
        return session.get_eligibility().on_benefits and data and "other-benefit" in data["benefits"]
