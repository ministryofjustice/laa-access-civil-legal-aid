from app.api import cla_backend
from flask import session


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


def get_payload(eligibility_data: dict) -> dict:
    about = eligibility_data.forms.get("about-you", {})
    benefits_form = eligibility_data.forms.get("benefits", {})

    benefits = benefits_form.get("benefits", [])

    payload = {
        "category": eligibility_data.category,
        "your_problem_notes": "",
        "notes": "",
        "property_set": [],
        "you": {
            "income": {
                "earnings": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "self_employment_drawings": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "benefits": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "tax_credits": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "child_benefits": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "maintenance_received": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "pension": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "other_income": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "self_employed": about.get("is_self_employed", False),
            },
            "savings": {
                "bank_balance": None,
                "investment_balance": None,
                "asset_balance": None,
                "credit_balance": None,
                "total": None,
            },
            "deductions": {
                "income_tax": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "national_insurance": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
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
            "income": {
                "earnings": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "self_employment_drawings": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "benefits": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "tax_credits": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "maintenance_received": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "pension": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "other_income": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "self_employed": about.get("is_partner_self_employed", False),
            },
            "savings": {
                "bank_balance": None,
                "investment_balance": None,
                "asset_balance": None,
                "credit_balance": None,
            },
            "deductions": {
                "income_tax": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
                "national_insurance": {
                    "per_interval_value": None,
                    "interval_period": "per_month",
                },
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
        "on_passported_benefits": False,
        "on_nass_benefits": False,
        "specific_benefits": {
            "pension_credit": "pension_credit" in benefits,
            "job_seekers_allowance": "job_seekers_allowance" in benefits,
            "employment_support": "employment_support" in benefits,
            "universal_credit": "universal_credit" in benefits,
            "income_support": "income_support" in benefits,
        },
        "disregards": [],
    }

    return payload
