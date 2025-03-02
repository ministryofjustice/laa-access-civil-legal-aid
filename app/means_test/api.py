from app.api import cla_backend
from flask import session
from app.means_test.forms.income import IncomeForm
from app.means_test.forms.benefits import BenefitsForm, AdditionalBenefitsForm
from app.means_test.forms.property import MultiplePropertiesForm
from app.means_test.forms.outgoings import OutgoingsForm
from app.means_test.money_interval import MoneyInterval
from app.means_test.constants import EligibilityStatus
import logging

logger = logging.getLogger(__name__)


def update_means_test(payload):
    means_test_endpoint = "checker/api/v1/eligibility_check/"

    ec_reference = session.get("reference")

    if ec_reference:
        response = cla_backend.patch(
            f"{means_test_endpoint}{ec_reference}", json=payload
        )
        return response
    else:
        response = cla_backend.post(means_test_endpoint, json=payload)
        session["reference"] = response["reference"]
        return response


def is_eligible(reference) -> EligibilityStatus:
    if not reference:
        raise ValueError("Reference cannot be empty")

    means_test_endpoint = "checker/api/v1/eligibility_check/"
    response = cla_backend.post(f"{means_test_endpoint}{reference}/is_eligible/")
    eligibility = EligibilityStatus.from_string(response["is_eligible"])
    return eligibility


def get_means_test_payload(eligibility_data) -> dict:
    about = eligibility_data.forms.get("about-you", {})
    savings_form = eligibility_data.forms.get("savings", {})

    has_partner = eligibility_data.forms.get("about-you", {}).get(
        "has_partner", False
    ) and not eligibility_data.forms.get("about-you", {}).get("in_dispute", False)
    is_employed = about.get("is_employed", None)
    is_self_employed = about.get("is_self_employed", None)
    is_partner_employed = about.get("is_partner_employed", None)
    is_partner_self_employed = about.get("is_partner_self_employed", None)

    # The below data code needs refactoring to only take in eligibility_data
    benefits_data = BenefitsForm.get_payload(eligibility_data.forms.get("benefits", {}))
    additional_benefits_data = AdditionalBenefitsForm.get_payload(
        eligibility_data.forms.get("additional-benefits", {})
    )
    income_data = IncomeForm(**eligibility_data.forms.get("income", {})).get_payload(
        employed=is_employed,
        self_employed=is_self_employed,
        partner_employed=is_partner_employed,
        partner_self_employed=is_partner_self_employed,
    )
    property_data = MultiplePropertiesForm.get_payload(
        eligibility_data.forms.get("property", {})
    )

    outgoings_data = OutgoingsForm.get_payload(
        eligibility_data.forms.get("outgoings", {})
    )

    # Sums rent to the other income field for you
    other_income = MoneyInterval(
        property_data.get("you").get("income", {}).get("other_income", 0)
    ) + income_data.get("you").get("income", {}).get("other_income", 0)

    payload = {
        "category": eligibility_data.category,
        "your_problem_notes": "",
        "notes": "",
        "property_set": property_data.get("property_set"),
        "you": {
            "income": {
                "earnings": income_data.get("you", {})
                .get("income", {})
                .get("earnings"),
                "self_employment_drawings": income_data.get("you", {})
                .get("income", {})
                .get("self_employment_drawings"),
                "tax_credits": income_data.get("you", {})
                .get("income", {})
                .get("tax_credits"),
                "maintenance_received": income_data.get("you", {})
                .get("income", {})
                .get("maintenance_received"),
                "pension": income_data.get("you", {}).get("income", {}).get("pension"),
                "other_income": other_income,
                "self_employed": is_self_employed,
                "benefits": additional_benefits_data.get("benefits"),
                "child_benefits": benefits_data.get("child_benefits"),
            },
            "savings": {
                "bank_balance": savings_form.get("savings", 0),
                "investment_balance": savings_form.get("investments", 0),
                "asset_balance": savings_form.get("valuables", 0),
                "credit_balance": None,
            },
            "deductions": {
                "income_tax": income_data.get("you", {})
                .get("deductions", {})
                .get("income_tax", MoneyInterval(0)),
                "national_insurance": income_data.get("you", {})
                .get("deductions", {})
                .get("national_insurance", MoneyInterval(0)),
                "maintenance": outgoings_data.get("maintenance", MoneyInterval(0)),
                "childcare": outgoings_data.get("childcare", MoneyInterval(0)),
                "mortgage": property_data.get("deductions", {}).get("mortgage", {}),
                "rent": outgoings_data.get("rent", MoneyInterval(0)),
                "criminal_legalaid_contributions": outgoings_data.get(
                    "income_contribution"
                ),
            },
        },
        "partner": {
            "income": {
                "earnings": income_data.get("partner", {})
                .get("income", {})
                .get("earnings"),
                "self_employment_drawings": income_data.get("partner", {})
                .get("income", {})
                .get("self_employment_drawings"),
                "tax_credits": income_data.get("partner", {})
                .get("income", {})
                .get("tax_credits"),
                "maintenance_received": income_data.get("partner", {})
                .get("income", {})
                .get("maintenance_received"),
                "pension": income_data.get("partner", {})
                .get("income", {})
                .get("pension"),
                "other_income": income_data.get("partner", {})
                .get("income", {})
                .get("other_income"),
                "self_employed": "0",
                "benefits": {
                    "per_interval_value": 0,
                    "per_interval_value_pounds": None,
                    "interval_period": "per_month",
                },
                "child_benefits": {
                    "per_interval_value": 0,
                    "per_interval_value_pounds": None,
                    "interval_period": "per_month",
                },
            },
            "savings": {
                "bank_balance": None,
                "investment_balance": None,
                "asset_balance": None,
                "credit_balance": None,
            },
            "deductions": {
                "income_tax": income_data.get("partner", {})
                .get("deductions", {})
                .get("income_tax", MoneyInterval(0)),
                "national_insurance": income_data.get("partner", {})
                .get("deductions", {})
                .get("national_insurance", MoneyInterval(0)),
                "maintenance": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "childcare": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "mortgage": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "rent": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "criminal_legalaid_contributions": None,
            },
        },
        "dependants_young": about.get("dependants_young", 0)
        if about.get("has_children", False)
        else 0,
        "dependants_old": about.get("dependants_old", 0)
        if about.get("has_dependants", False)
        else 0,
        "is_you_or_your_partner_over_60": about.get("aged_60_or_over", False),
        "has_partner": has_partner,
        "on_passported_benefits": benefits_data["on_passported_benefits"],
        "on_nass_benefits": additional_benefits_data["on_nass_benefits"],
        "specific_benefits": benefits_data["specific_benefits"],
        "disregards": [],
    }

    if not has_partner:
        del payload["partner"]

    return payload
