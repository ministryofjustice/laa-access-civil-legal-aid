from flask.views import View, MethodView
from flask import render_template, url_for, redirect, session, request
from werkzeug.datastructures import MultiDict

from app.means_test.api import update_means_test
from app.means_test.forms.about_you import AboutYouForm
from app.means_test.forms.money import ExampleForm
from app.means_test.forms.benefits import BenefitsForm, AdditionalBenefitsForm
from app.means_test.forms.property import PropertyForm
from app.means_test.utils import MoneyInterval


class MeansTest(View):
    forms = {
        "about-you": AboutYouForm,
        "benefits": BenefitsForm,
        "additional-benefits": AdditionalBenefitsForm,
        "property": PropertyForm,
        "money": ExampleForm,
    }

    def __init__(self, current_form_class, current_name):
        self.form_class = current_form_class
        self.current_name = current_name

    def dispatch_request(self):
        eligibility = session.get_eligibility()
        form_data = MultiDict(eligibility.forms.get(self.current_name, {}))

        form = self.form_class(request.form or form_data)
        if form.validate_on_submit():
            eligibility.add(self.current_name, form.data)
            next_page = url_for(f"means_test.{self.get_next_page(self.current_name)}")
            payload = self.get_payload(eligibility)
            update_means_test(payload)

            return redirect(next_page)
        return render_template(self.form_class.template, form=form)

    def get_next_page(self, current_key):
        keys = list(self.forms.keys())  # Convert to list for easier indexing
        try:
            current_index = keys.index(current_key)
            # Look through remaining pages
            for next_key in keys[current_index + 1 :]:
                if self.forms[next_key].should_show():
                    return next_key
            return "review"  # No more valid pages found
        except ValueError:  # current_key not found
            return "review"

    @classmethod
    def get_payload(cls, eligibility_data: dict) -> dict:
        about = eligibility_data.forms.get("about-you", {})
        benefits_form = eligibility_data.forms.get(
            "benefits", {"benefits": [], "child_benefits": None}
        )
        child_benefits = MoneyInterval(0)
        if "child_benefit" in benefits_form["benefits"]:
            child_benefits = MoneyInterval(benefits_form["child_benefits"])

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
                    "child_benefits": child_benefits,
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
            "on_passported_benefits": eligibility_data.is_passported,
            "on_nass_benefits": False,
            "specific_benefits": eligibility_data.specific_benefits,
            "disregards": [],
        }

        return payload


class CheckYourAnswers(MethodView):
    def get(self):
        return render_template("means_test/review.html", data=session.get_eligibility())
