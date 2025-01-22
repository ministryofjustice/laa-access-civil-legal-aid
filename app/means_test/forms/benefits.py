from flask import session
from flask_babel import gettext as _
from wtforms.validators import InputRequired
from app.means_test.widgets import MeansTestCheckboxInput, MeansTestRadioInput
from app.means_test.forms import BaseMeansTestForm
from app.means_test.fields import MoneyField, MoneyFieldWidgetWidget
from app.means_test.partner_fields import PartnerMultiCheckboxField, PartnerYesNoField
from app.means_test.validators import (
    MoneyIntervalAmountRequired,
    ValidateIfSession,
    ValidateIf,
    ValidateIfType,
)
from app.means_test.data import BenefitsData
from app.means_test import YES, NO


def get_benefits_choices():
    choices = BenefitsData.BENEFITS_CHOICES.copy()
    # Add the OR text in
    choices.insert(-1, ("", ""))
    return choices


class BenefitsForm(BaseMeansTestForm):
    title = _(" Which benefits do you receive?")

    template = "means_test/benefits.html"

    benefits = PartnerMultiCheckboxField(
        label=_("Which benefits do you receive?"),
        partner_label=_("Which benefits do you and your partner receive?"),
        widget=MeansTestCheckboxInput(
            is_inline=False, show_divider=True, hint_text=_("Select all that apply")
        ),
        choices=get_benefits_choices(),
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

    @property
    def data(self):
        # Only return data for our fields and not including the core fields
        data = super().data
        return {
            key: value
            for key, value in data.items()
            if key not in ["csrf_token", "submit"]
        }

    @classmethod
    def should_show(cls) -> bool:
        return session.get("eligibility").on_benefits

    def render_conditional(self, field, sub_field, conditional_value):
        sub_field_rendered = sub_field()
        conditional = {"value": conditional_value, "html": sub_field_rendered}
        field.render_kw = {"conditional": conditional}
        return field()


class AdditionalBenefitsForm(BaseMeansTestForm):
    title = _("Your additional benefits")
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
            hint_text=_(
                "These benefits don’t count as income. Please tick the ones you receive."
            ),
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
        partner_label=_(
            "Do you or your partner receive any other benefits not listed above? "
        ),
        description=_(
            "For example, National Asylum Support Service Benefit, "
            "Incapacity Benefit, Contribution-based Jobseeker’s "
            "Allowance"
        ),
        widget=MeansTestRadioInput(),
        choices=[(YES, _("Yes")), (NO, _("No"))],
        validators=[
            InputRequired(message=_("Tell us whether you receive any other benefits"))
        ],
    )
    total_other_benefit = MoneyField(
        label=_("If Yes, total amount of benefits not listed above"),
        exclude_intervals=["per_month"],
        widget=MoneyFieldWidgetWidget(),
        validators=[
            ValidateIf("other_benefits", YES),
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
        return {
            key: value
            for key, value in data.items()
            if key not in ["csrf_token", "submit"]
        }

    @classmethod
    def should_show(cls) -> bool:
        data = session.get("eligibility").forms.get("benefits")
        return data and "other-benefit" in data["benefits"]
