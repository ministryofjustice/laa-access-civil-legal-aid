from flask.views import View, MethodView
from flask import render_template, url_for, redirect, session

from app.means_test.api import update_means_test
from app.means_test.forms import BenefitsForm, AboutYouForm


class MeansTest(View):
    forms = {"about-you": AboutYouForm, "benefits": BenefitsForm}

    def __init__(self, current_form_class, current_name):
        self.form_class = current_form_class
        self.current_name = current_name

    def dispatch_request(self):
        form = self.form_class()
        if form.validate_on_submit():
            session.get_eligibility().add(self.current_name, form.data)
            next_page = url_for(f"means_test.{self.get_next_page(self.current_name)}")
            payload = self.get_payload(session.get_eligibility())
            update_means_test(payload)

            return redirect(next_page)
        return render_template(self.form_class.template, form=form)

    def get_next_page(self, current_key):
        keys = iter(self.forms.keys())  # Create an iterator over the keys
        for key in keys:
            if key == current_key:
                next_page = next(
                    keys, None
                )  # Return the next key or None if no more keys
                if not next_page:
                    return "review"
                next_page_form = self.forms[next_page]
                if next_page_form.should_show():
                    return next_page
                continue
        return "review"

    @classmethod
    def get_payload(cls, eligibility_data: dict) -> dict:
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


class CheckYourAnswers(MethodView):
    def get(self):
        return render_template("means_test/review.html", data=session.get_eligibility())
