from flask import session
from flask_babel import gettext as _
from wtforms.fields import SelectMultipleField
from app.means_test.widgets import MeansTestCheckboxInput
from app.means_test.forms import BaseMeansTestForm
from app.means_test.fields import MoneyField, MoneyFieldWidgetWidget
from app.means_test.validators import (
    MoneyIntervalAmountRequired,
    ValidateIfSession,
    ValidateIf,
    ValidateIfType,
)


class BenefitsForm(BaseMeansTestForm):
    title = _(" Which benefits do you receive?")

    template = "means_test/benefits.html"

    benefits = SelectMultipleField(
        label="",
        widget=MeansTestCheckboxInput(
            is_inline=False, show_divider=True, hint_text=_("Select all that apply")
        ),
        choices=[
            ("child_benefit", _("Child Benefit")),
            ("pension_credit", _("Guarantee Credit")),
            ("income_support", _("Income Support")),
            ("job_seekers_allowance", _("Income-based Jobseeker's Allowance")),
            (
                "employment_support",
                _("Income-related Employment and Support Allowance"),
            ),
            ("universal_credit", _("Universal Credit")),
            ("", ""),
            ("other-benefit", _("Any other benefits")),
        ],
    )

    child_benefits = MoneyField(
        _("If yes, enter the total amount you get for all your children"),
        hint_text=_("For example, £32.18 per week"),
        exclude_intervals=["per_month", "per_year"],
        widget=MoneyFieldWidgetWidget(),
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
            self.benefits.choices = list(
                filter(
                    lambda benefit: benefit[0] != "child_benefit", self.benefits.choices
                )
            )

    @classmethod
    def should_show(cls) -> bool:
        return session.get("eligibility").on_benefits

    def render_conditional(self, field, sub_field, conditional_value):
        sub_field_rendered = sub_field()
        conditional = {"value": conditional_value, "html": sub_field_rendered}
        field.render_kw = {"conditional": conditional}
        return field()


class AdditionalBenefitsForm(BaseMeansTestForm):
    title = _(" Your additional benefits")
    description = _(
        "You’ll need to provide evidence of the financial information you’ve given us through this service."
    )
    template = "means_test/benefits.html"
    benefits = SelectMultipleField(
        label=_("Do you get any of these benefits?"),
        widget=MeansTestCheckboxInput(
            is_inline=False, show_divider=False, hint_text=_("Select all that apply")
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

    @classmethod
    def should_show(cls) -> bool:
        data = session.get("eligibility").forms.get("benefits")
        return data and "other-benefit" in data["benefits"]
