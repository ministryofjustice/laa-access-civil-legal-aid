from flask import session
from flask_babel import gettext as _
from wtforms.fields import SelectMultipleField
from app.means_test.widgets import MeansTestCheckboxInput
from app.means_test.forms import BaseMeansTestForm
from app.means_test import YES


class BenefitsForm(BaseMeansTestForm):
    title = _(" Which benefits do you receive?")

    template = "means_test/benefits.html"

    @classmethod
    def should_show(cls) -> bool:
        return (
            session.get_eligibility().forms.get("about-you", {}).get("on_benefits")
            == YES
        )

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
