from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class EligibilityData:
    def __init__(self, category: str, forms: Dict, notes: Optional[Dict] = None):
        self.category = category
        self.forms = forms
        self.notes = notes


ABOUT_YOU_TEST_CASES = [
    {
        "id": "basic_no_benefits_no_partner",
        "name": "basic_no_benefits_no_partner",
        "description": "Basic case with no benefits or partner",
        "input": EligibilityData(
            category="immigration",
            notes={"User problem": "test"},
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
            "notes": "User problem:\ntest",
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
        },
    },
    {
        "id": "with_partner_and_benefits",
        "name": "with_partner_and_benefits",
        "description": "Case with partner and universal credit and pension credit benefits",
        "input": EligibilityData(
            category="debt",
            notes={"User problem": "test"},
            forms={
                "about-you": {
                    "is_self_employed": True,
                    "has_partner": True,
                    "in_dispute": False,
                    "has_children": False,
                    "aged_60_or_over": False,
                    "is_partner_self_employed": True,
                },
                "benefits": {"benefits": ["universal_credit", "pension_credit"]},
            },
        ),
        "expected": {
            "category": "debt",
            "notes": "User problem:\ntest",
            "has_partner": True,
            "dependants_young": 0,
            "dependants_old": 0,
            "is_you_or_your_partner_over_60": False,
            "on_nass_benefits": False,
            "specific_benefits": {
                "pension_credit": True,
                "job_seekers_allowance": False,
                "employment_support": False,
                "universal_credit": True,
                "income_support": False,
            },
        },
    },
    {
        "id": "with_dependants",
        "name": "with_dependants",
        "description": "Case with young and old dependants and income support",
        "input": EligibilityData(
            category="family",
            notes={"User problem": "test"},
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
            "notes": "User problem:\ntest",
            "has_partner": False,
            "dependants_young": 2,
            "dependants_old": 1,
            "is_you_or_your_partner_over_60": False,
            "on_nass_benefits": False,
            "specific_benefits": {
                "pension_credit": False,
                "job_seekers_allowance": False,
                "employment_support": False,
                "universal_credit": False,
                "income_support": True,
            },
        },
    },
    {
        "id": "no_forms",
        "name": "no_forms",
        "description": "Edge case with no forms present",
        "input": EligibilityData(
            category="immigration", notes={"User problem": "test"}, forms={}
        ),
        "expected": {
            "category": "immigration",
            "notes": "User problem:\ntest",
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
        },
    },
]

INCOME_TEST_CASES = [
    {
        "id": "basic_employed_no_partner",
        "name": "basic_employed_no_partner",
        "description": "Basic case with employed person, no partner",
        "input": EligibilityData(
            category="debt",
            notes={"User problem": "test"},
            forms={
                "about-you": {
                    "is_employed": True,
                    "is_self_employed": False,
                    "has_partner": False,
                    "in_dispute": False,
                },
                "income": {
                    "earnings": {
                        "per_interval_value": 200000,
                        "per_interval_value_pounds": 2000.00,
                        "interval_period": "per_month",
                    },
                    "income_tax": {
                        "per_interval_value": 40000,
                        "per_interval_value_pounds": 400.00,
                        "interval_period": "per_month",
                    },
                    "national_insurance": {
                        "per_interval_value": 20000,
                        "per_interval_value_pounds": 200.00,
                        "interval_period": "per_month",
                    },
                    "working_tax_credit": {
                        "per_interval_value": 10000,
                        "per_interval_value_pounds": 100.00,
                        "interval_period": "per_month",
                    },
                    "maintenance_received": {
                        "per_interval_value": 0,
                        "per_interval_value_pounds": 0.00,
                        "interval_period": "per_month",
                    },
                },
            },
        ),
        "expected": {
            "you": {
                "income": {
                    "earnings": {
                        "per_interval_value": 200000,
                        "interval_period": "per_month",
                    },
                    "self_employment_drawings": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                    "tax_credits": {
                        "per_interval_value": 10000,
                        "interval_period": "per_month",
                    },
                    "maintenance_received": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                    "pension": {
                        "per_interval_value": None,
                        "interval_period": None,
                    },
                    "other_income": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                },
                "deductions": {
                    "income_tax": {
                        "per_interval_value": 40000,
                        "interval_period": "per_month",
                    },
                    "national_insurance": {
                        "per_interval_value": 20000,
                        "interval_period": "per_month",
                    },
                },
            }
        },
    },
    {
        "id": "self_employed_with_mixed_intervals",
        "name": "self_employed_with_mixed_intervals",
        "description": "Self-employed person with income in different intervals",
        "input": EligibilityData(
            category="debt",
            notes={"User problem": "test"},
            forms={
                "about-you": {
                    "is_employed": False,
                    "is_self_employed": True,
                    "has_partner": False,
                    "in_dispute": False,
                },
                "income": {
                    "earnings": {
                        "per_interval_value": 300000,
                        "per_interval_value_pounds": 3000.00,
                        "interval_period": "per_month",
                    },
                    "income_tax": {
                        "per_interval_value": 15000,
                        "per_interval_value_pounds": 150.00,
                        "interval_period": "per_week",
                    },
                    "national_insurance": {
                        "per_interval_value": 50000,
                        "per_interval_value_pounds": 500.00,
                        "interval_period": "per_4week",
                    },
                    "working_tax_credit": {
                        "per_interval_value": 120000,
                        "per_interval_value_pounds": 1200.00,
                        "interval_period": "per_year",
                    },
                    "maintenance_received": {
                        "per_interval_value": 5000,
                        "per_interval_value_pounds": 50.00,
                        "interval_period": "per_year",
                    },
                    "pension": {
                        "per_interval_value": 10000,
                        "per_interval_value_pounds": 1000.00,
                        "interval_period": "per_month",
                    },
                    "other_income": {
                        "per_interval_value": 25000,
                        "per_interval_value_pounds": 250.00,
                        "interval_period": "per_month",
                    },
                },
            },
        ),
        "expected": {
            "you": {
                "income": {
                    "earnings": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                    "self_employment_drawings": {
                        "per_interval_value": 300000,
                        "interval_period": "per_month",
                    },
                    "tax_credits": {
                        "per_interval_value": 10000,
                        "interval_period": "per_month",
                    },
                    "maintenance_received": {
                        "per_interval_value": 5000,
                        "interval_period": "per_year",
                    },
                    "pension": {
                        "per_interval_value": 10000,
                        "interval_period": "per_month",
                    },
                    "other_income": {
                        "per_interval_value": 25000,
                        "interval_period": "per_month",
                    },
                    "self_employed": True,
                },
                "deductions": {
                    "income_tax": {
                        "per_interval_value": 15000,
                        "interval_period": "per_week",
                    },
                    "national_insurance": {
                        "per_interval_value": 50000,
                        "interval_period": "per_4week",
                    },
                },
            }
        },
    },
    {
        "id": "partner_case_with_child_tax",
        "name": "partner_case_with_child_tax",
        "description": "Case with partner and child tax credits",
        "input": EligibilityData(
            category="debt",
            notes={"User problem": "test"},
            forms={
                "about-you": {
                    "is_employed": True,
                    "is_self_employed": False,
                    "has_partner": True,
                    "in_dispute": False,
                    "is_partner_employed": False,
                    "is_partner_self_employed": True,
                },
                "income": {
                    "earnings": {
                        "per_interval_value": 250000,
                        "per_interval_value_pounds": 2500.00,
                        "interval_period": "per_month",
                    },
                    "child_tax_credit": {
                        "per_interval_value": 30000,
                        "per_interval_value_pounds": 300.00,
                        "interval_period": "per_month",
                    },
                    "working_tax_credit": {
                        "per_interval_value": 10000,
                        "per_interval_value_pounds": 100.00,
                        "interval_period": "per_month",
                    },
                    "partner_earnings": {
                        "per_interval_value": 200000,
                        "per_interval_value_pounds": 2000.00,
                        "interval_period": "per_month",
                    },
                    "maintenance_received": {
                        "per_interval_value": 0,
                        "per_interval_value_pounds": 0,
                        "interval_period": "per_month",
                    },
                    "pension": {
                        "per_interval_value": 0,
                        "per_interval_value_pounds": 0,
                        "interval_period": "per_month",
                    },
                    "other_income": {
                        "per_interval_value": 1000,
                        "per_interval_value_pounds": 0,
                        "interval_period": "per_month",
                    },
                    "income_tax": {
                        "per_interval_value": 2000,
                        "interval_period": "per_month",
                    },
                    "national_insurance": {
                        "per_interval_value": 3000,
                        "interval_period": "per_month",
                    },
                    "partner_working_tax_credit": {
                        "per_interval_value": 50,
                        "interval_period": "per_month",
                    },
                    "partner_maintenance_received": {
                        "per_interval_value": 50,
                        "interval_period": "per_month",
                    },
                    "partner_pension": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                    "partner_other_income": {
                        "per_interval_value": 1000,
                        "interval_period": "per_month",
                    },
                    "partner_income_tax": {
                        "per_interval_value": 2500,
                        "interval_period": "per_month",
                    },
                    "partner_national_insurance": {
                        "per_interval_value": 3500,
                        "interval_period": "per_month",
                    },
                },
            },
        ),
        "expected": {
            "you": {
                "income": {
                    "earnings": {
                        "per_interval_value": 250000,
                        "interval_period": "per_month",
                    },
                    "self_employment_drawings": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                    "tax_credits": {
                        "per_interval_value": 40000,
                        "interval_period": "per_month",
                    },  # Combined child + working tax
                    "maintenance_received": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                    "pension": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                    "other_income": {
                        "per_interval_value": 1000,
                        "interval_period": "per_month",
                    },
                },
                "deductions": {
                    "income_tax": {
                        "per_interval_value": 2000,
                        "interval_period": "per_month",
                    },
                    "national_insurance": {
                        "per_interval_value": 3000,
                        "interval_period": "per_month",
                    },
                },
            },
            "partner": {
                "income": {
                    "earnings": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                    "self_employment_drawings": {
                        "per_interval_value": 200000,
                        "interval_period": "per_month",
                    },
                    "tax_credits": {
                        "per_interval_value": 50,
                        "interval_period": "per_month",
                    },
                    "maintenance_received": {
                        "per_interval_value": 50,
                        "interval_period": "per_month",
                    },
                    "pension": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                    "other_income": {
                        "per_interval_value": 1000,
                        "interval_period": "per_month",
                    },
                },
                "deductions": {
                    "income_tax": {
                        "per_interval_value": 2500,
                        "interval_period": "per_month",
                    },
                    "national_insurance": {
                        "per_interval_value": 3500,
                        "interval_period": "per_month",
                    },
                },
            },
        },
    },
]

SAVINGS_TEST_CASES = [
    {
        "id": "no_savings",
        "name": "no_savings",
        "description": "Case with no savings",
        "input": EligibilityData(
            category="debt",
            notes={"User problem": "test"},
            forms={
                "about-you": {
                    "is_employed": False,
                    "is_self_employed": False,
                    "has_partner": False,
                    "in_dispute": False,
                },
            },
        ),
        "expected": {"you": {}},
    },
    {
        "id": "savings",
        "name": "savings",
        "description": "Case with savings",
        "input": EligibilityData(
            category="debt",
            notes={"User problem": "test"},
            forms={
                "about-you": {
                    "is_employed": False,
                    "is_self_employed": False,
                    "has_partner": False,
                    "in_dispute": False,
                },
                "savings": {
                    "savings": 5001,
                    "investments": 6001,
                    "valuables": 7001,
                    "credit_balance": None,
                },
            },
        ),
        "expected": {
            "you": {
                "savings": {
                    "bank_balance": 5001,
                    "investment_balance": 6001,
                    "asset_balance": 7001,
                    "credit_balance": None,
                }
            }
        },
    },
]


OUTGOINGS_TEST_CASES = [
    {
        "id": "no_outgoings",
        "name": "no_outgoings",
        "description": "Case with no outgoings",
        "input": EligibilityData(
            category="debt",
            notes={"User problem": "test"},
            forms={
                "about-you": {
                    "is_employed": False,
                    "is_self_employed": False,
                    "has_partner": False,
                    "in_dispute": False,
                },
            },
        ),
        "expected": {"you": {}},
    },
    {
        "id": "outgoings",
        "name": "outgoings",
        "description": "Case with outgoings",
        "input": EligibilityData(
            category="debt",
            notes={"User problem": "test"},
            forms={
                "about-you": {
                    "is_employed": False,
                    "is_self_employed": False,
                    "has_partner": False,
                    "in_dispute": False,
                },
                "outgoings": {
                    "maintenance": {
                        "per_interval_value": 250000,
                        "per_interval_value_pounds": 2500.00,
                        "interval_period": "per_month",
                    },
                    "childcare": {
                        "per_interval_value": 250000,
                        "per_interval_value_pounds": 2500.00,
                        "interval_period": "per_month",
                    },
                    "rent": {
                        "per_interval_value": 250000,
                        "per_interval_value_pounds": 2500.00,
                        "interval_period": "per_month",
                    },
                    "income_contribution": 7005,
                },
            },
        ),
        "expected": {
            "you": {
                "deductions": {
                    "maintenance": {
                        "per_interval_value": 250000,
                        "interval_period": "per_month",
                    },
                    "childcare": {
                        "per_interval_value": 250000,
                        "interval_period": "per_month",
                    },
                    "rent": {
                        "per_interval_value": 250000,
                        "interval_period": "per_month",
                    },
                    "criminal_legalaid_contributions": 7005,
                }
            }
        },
    },
]
