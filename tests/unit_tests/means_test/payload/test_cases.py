from dataclasses import dataclass
from typing import Dict


@dataclass
class EligibilityData:
    category: str
    forms: Dict


TEST_CASES = [
    {
        "id": "basic_no_benefits_no_partner",
        "name": "basic_no_benefits_no_partner",
        "description": "Basic case with no benefits or partner",
        "input": EligibilityData(
            category="immigration",
            forms={
                "about-you": {
                    "is_self_employed": False,
                    "has_partner": False,
                    "in_dispute": False,
                    "has_children": False,
                    "has_dependants": False,
                    "aged_60_or_over": False,
                },
                "benefits": {"benefits": []},
            },
        ),
        "expected": {
            "category": "immigration",
            "has_partner": False,
            "dependants_young": 0,
            "dependants_old": 0,
            "is_you_or_your_partner_over_60": False,
            "on_passported_benefits": False,
            "on_nass_benefits": False,
            "specific_benefits": {
                "pension_credit": False,
                "job_seekers_allowance": False,
                "employment_support": False,
                "universal_credit": False,
                "income_support": False,
            },
            "you": {"income": {"self_employed": False}},
        },
    },
    {
        "id": "with_partner_and_benefits",
        "name": "with_partner_and_benefits",
        "description": "Case with partner and universal credit and pension credit benefits",
        "input": EligibilityData(
            category="debt",
            forms={
                "about-you": {
                    "is_self_employed": True,
                    "has_partner": True,
                    "in_dispute": True,
                    "has_children": False,
                    "aged_60_or_over": False,
                    "is_partner_self_employed": True,
                },
                "benefits": {"benefits": ["universal_credit", "pension_credit"]},
            },
        ),
        "expected": {
            "category": "debt",
            "has_partner": True,
            "dependants_young": 0,
            "dependants_old": 0,
            "is_you_or_your_partner_over_60": False,
            "on_passported_benefits": False,
            "on_nass_benefits": False,
            "specific_benefits": {
                "pension_credit": True,
                "job_seekers_allowance": False,
                "employment_support": False,
                "universal_credit": True,
                "income_support": False,
            },
            "you": {"income": {"self_employed": True}},
            "partner": {"income": {"self_employed": True}},
        },
    },
    {
        "id": "with_dependants",
        "name": "with_dependants",
        "description": "Case with young and old dependants and income support",
        "input": EligibilityData(
            category="family",
            forms={
                "about-you": {
                    "is_self_employed": False,
                    "has_partner": False,
                    "in_dispute": False,
                    "has_children": True,
                    "has_dependants": True,
                    "dependants_young": 2,
                    "dependants_old": 1,
                    "aged_60_or_over": False,
                },
                "benefits": {"benefits": ["income_support"]},
            },
        ),
        "expected": {
            "category": "family",
            "has_partner": False,
            "dependants_young": 2,
            "dependants_old": 1,
            "is_you_or_your_partner_over_60": False,
            "on_passported_benefits": False,
            "on_nass_benefits": False,
            "specific_benefits": {
                "pension_credit": False,
                "job_seekers_allowance": False,
                "employment_support": False,
                "universal_credit": False,
                "income_support": True,
            },
            "you": {"income": {"self_employed": False}},
        },
    },
    {
        "id": "no_forms",
        "name": "no_forms",
        "description": "Edge case with no forms present",
        "input": EligibilityData(category="immigration", forms={}),
        "expected": {
            "category": "immigration",
            "has_partner": False,
            "dependants_young": 0,
            "dependants_old": 0,
            "is_you_or_your_partner_over_60": False,
            "on_passported_benefits": False,
            "on_nass_benefits": False,
            "specific_benefits": {
                "pension_credit": False,
                "job_seekers_allowance": False,
                "employment_support": False,
                "universal_credit": False,
                "income_support": False,
            },
            "you": {"income": {"self_employed": False}},
        },
    },
]
