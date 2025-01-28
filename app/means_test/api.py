from app.api import cla_backend
from flask import session
from app.means_test.forms.income import IncomeForm
from app.means_test.forms.property import PropertiesPayload
from app.means_test.money_interval import MoneyInterval
from tests.unit_tests.means_test.payload.test_cases import EligibilityData
from app.means_test.data import BenefitsData, AdditionalBenefitData


def deep_update(original, updates):
    """
    Recursively updates a nested dictionary with values from another dictionary.
    Only updates keys present in the `updates` dictionary.
    """
    for key, value in updates.items():
        if (
            isinstance(value, dict)
            and key in original
            and isinstance(original[key], dict)
        ):
            deep_update(original[key], value)  # Recursive call for nested dict
        else:
            original[key] = value


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


def is_eligible(reference):
    means_test_endpoint = "checker/api/v1/eligibility_check/"
    response = cla_backend.post(f"{means_test_endpoint}{reference}/is_eligible/")
    return response["is_eligible"]


def get_means_test_payload(eligibility_data: EligibilityData) -> dict:
    about = eligibility_data.forms.get("about-you", {})

    income_form = eligibility_data.forms.get("income", {})
    property_form = eligibility_data.forms.get("property", {})
    benefits = BenefitsData(**eligibility_data.forms.get("benefits", {})).to_payload()

    additional_benefits = AdditionalBenefitData(
        **eligibility_data.forms.get("additional-benefits", {})
    ).to_payload()

    has_partner = eligibility_data.forms.get("about-you", {}).get(
        "has_partner", False
    ) and not eligibility_data.forms.get("about-you", {}).get("in_dispute", False)
    is_employed = about.get("is_employed", None)
    is_self_employed = about.get("is_self_employed", None)
    is_partner_employed = about.get("is_partner_employed", None)
    is_partner_self_employed = about.get("is_partner_self_employed", None)

    income_data: dict[str, dict] = IncomeForm(**income_form).get_payload(
        employed=is_employed,
        self_employed=is_self_employed,
        partner_employed=is_partner_employed,
        partner_self_employed=is_partner_self_employed,
    )

    you_income = income_data.get("you", {}).get("income", {})
    you_income.update(
        {
            "benefits": additional_benefits["benefits"],
            "child_benefits": benefits["child_benefits"],
        }
    )

    # Remove rent field from property set and setup payload
    if eligibility_data.forms.get("about-you", {}).get("own_property"):
        property_payload = PropertiesPayload(property_form)
        for property_item in property_payload.get("property_set", []):
            property_item.pop("rent", None)

    payload = {
        "category": eligibility_data.category,
        "your_problem_notes": "",
        "notes": "",
        "property_set": [],
        "you": {
            "income": you_income,
            "savings": {
                "bank_balance": None,
                "investment_balance": None,
                "asset_balance": None,
                "credit_balance": None,
                "total": None,
            },
            "deductions": {
                "income_tax": income_data.get("you", {})
                .get("deductions", {})
                .get("income_tax", MoneyInterval(0)),
                "national_insurance": income_data.get("you", {})
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
        "partner": {
            "income": income_data.get("partner", {}).get("income", {}),
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
        "has_partner": about.get("has_partner", False)
        and about.get("in_dispute", False),
        "on_passported_benefits": benefits["on_passported_benefits"],
        "on_nass_benefits": additional_benefits["on_nass_benefits"],
        "specific_benefits": benefits["specific_benefits"],
        "disregards": [],
    }

    # Add in the property payload
    if eligibility_data.forms.get("about-you", {}).get("own_property"):
        deep_update(payload, property_payload)

    if not has_partner:
        del payload["partner"]

    return payload
