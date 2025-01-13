from flask_babel import lazy_gettext as _
from flask import session
from wtforms import SelectMultipleField
from app.means_test.forms.widgets import MeansTestCheckboxInput
from . import BaseMeansTestForm


class BenefitsForm(BaseMeansTestForm):
    title = _(" Which benefits do you receive?")
    benefits = SelectMultipleField(
        label="",
        widget=MeansTestCheckboxInput(
            is_inline=False, show_divider=True, hint_text=_("Select all that apply")
        ),
        choices=[
            ("child_benefit", _("Child Benefit")),
            ("pension_credit", _("Guarantee Credit")),
            ("income_support", _("Income Support")),
            ("job_seekers_allowance", _("Income-based Jobseeker’s Allowance")),
            (
                "employment_support",
                _("Income-related Employment and Support Allowance"),
            ),
            ("universal_credit", _("Universal Credit")),
            ("", ""),
            ("other-benefit", _("Any other benefits")),
        ],
    )

    def __init__(self, *args, **kwargs):
        if not (session.has_children or session.has_dependants):
            choices = self.benefits.kwargs["choices"]
            self.benefits.kwargs["choices"] = filter(
                lambda benefit: benefit[0] != "child_benefit", choices
            )
        super().__init__(*args, **kwargs)


class AdditionalBenefitsForm(BaseMeansTestForm):
    title = _(" Your additional benefits")
    description = _(
        "You’ll need to provide evidence of the financial information you’ve given us through this service."
    )
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
