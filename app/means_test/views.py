from flask.views import View, MethodView
from flask import render_template, url_for, redirect, session, request

from werkzeug.datastructures import MultiDict

from app.means_test.api import update_means_test, get_means_test_payload
from app.means_test.forms.about_you import AboutYouForm
from app.means_test.forms.benefits import BenefitsForm, AdditionalBenefitsForm
from app.means_test.forms.property import MultiplePropertiesForm
from app.means_test.forms.income import IncomeForm


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


class MeansTest(View):
    forms = {
        "about-you": AboutYouForm,
        "benefits": BenefitsForm,
        "property": MultiplePropertiesForm,
        "additional-benefits": AdditionalBenefitsForm,
        "income": IncomeForm,
    }

    def __init__(self, current_form_class, current_name):
        self.form_class = current_form_class
        self.current_name = current_name

    def handle_multiple_properties_ajax_request(self, form):
        if "add-property" in request.form:
            form.properties.append_entry()
            form._submitted = False
            return render_template(self.form_class.template, form=form)

        # Handle removing a property
        elif "remove-property-2" in request.form or "remove-property-3" in request.form:
            form.properties.pop_entry()
            form._submitted = False
            return render_template(self.form_class.template, form=form)

        return None

    def dispatch_request(self):
        eligibility = session.get_eligibility()
        form_data = MultiDict(eligibility.forms.get(self.current_name, {}))
        form = self.form_class(request.form or form_data)
        if isinstance(form, MultiplePropertiesForm):
            response = self.handle_multiple_properties_ajax_request(form)
            if response is not None:
                return response

        if form.validate_on_submit():
            session.get_eligibility().add(self.current_name, form.data)
            next_page = url_for(f"means_test.{self.get_next_page(self.current_name)}")
            payload = get_means_test_payload(session.get_eligibility())
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


"""
    @classmethod
    def get_payload(cls, eligibility_data: dict) -> dict:
        about = eligibility_data.forms.get("about-you", {})
        property_form = eligibility_data.forms.get("property", {})

        benefits = BenefitsData(
            **eligibility_data.forms.get("benefits", {})
        ).to_payload()

        additional_benefits = AdditionalBenefitData(
            **eligibility_data.forms.get("additional-benefits", {})
        ).to_payload()

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
                "income": {
                    "earnings": {
                        "per_interval_value": None,
                        "interval_period": "per_month",
                    },
                    "self_employment_drawings": {
                        "per_interval_value": None,
                        "interval_period": "per_month",
                    },
                    "benefits": additional_benefits["benefits"],
                    "tax_credits": {
                        "per_interval_value": None,
                        "interval_period": "per_month",
                    },
                    "child_benefits": benefits["child_benefits"],
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
            "on_passported_benefits": benefits["on_passported_benefits"],
            "on_nass_benefits": additional_benefits["on_nass_benefits"],
            "specific_benefits": benefits["specific_benefits"],
            "disregards": [],
        }

        # Add in the property payload
        if eligibility_data.forms.get("about-you", {}).get("own_property"):
            deep_update(payload, property_payload)

        return payload
"""


class CheckYourAnswers(MethodView):
    def get(self):
        return render_template("means_test/review.html", data=session.get_eligibility())
