from dataclasses import dataclass, field
from flask_babel import lazy_gettext as _
from app.means_test.utils import MoneyInterval
from app.means_test import is_yes


@dataclass
class BenefitsData:
    BENEFITS_CHOICES = [
        ("child_benefit", _("Child Benefit")),
        ("pension_credit", _("Guarantee Credit")),
        ("income_support", _("Income Support")),
        ("job_seekers_allowance", _("Income-based Jobseeker’s Allowance")),
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

    def to_payload(self):
        payload = {
            "specific_benefits": self.specific_benefits,
            "on_passported_benefits": self.is_passported,
        }
        child_benefits = MoneyInterval(0)
        if "child_benefit" in self.benefits and not self.is_passported:
            child_benefits = MoneyInterval(self.child_benefits)

        payload["child_benefits"] = child_benefits.to_json()
        return payload


@dataclass
class AdditionalBenefitData:
    benefits: list = field(default_factory=list)
    other_benefits: list = field(default_factory=list)
    total_other_benefit: dict = field(default_factory=dict)

    def to_payload(self):
        other_benefits_total = MoneyInterval(0)
        if is_yes(self.other_benefits):
            other_benefits_total = MoneyInterval(self.total_other_benefit)

        payload = {
            "on_nass_benefits": False,  # Always False, asylum-support is no longer a benefit selection
            "benefits": other_benefits_total.to_json(),
        }
        return payload
