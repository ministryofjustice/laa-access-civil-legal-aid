from flask.views import View, MethodView
from flask import render_template, url_for, redirect, session, request

from app.means_test import YES, NO
from app.means_test.api import update_means_test
from app.means_test.forms.about_you import AboutYouForm
from app.means_test.forms.benefits import BenefitsForm
from app.means_test.forms.property import MultiplePropertiesForm
from app.means_test.money_interval import MoneyInterval, to_amount


def mi(field, val):
    amount = "%s-per_interval_value" % field
    period = "%s-interval_period" % field
    return {"per_interval_value": val(amount), "interval_period": val(period)}


class PropertyPayload(dict):
    def __init__(self, form_data={}):
        super(PropertyPayload, self).__init__()

        def val(field):
            return form_data.get(field)

        def yes(field):
            return form_data.get(field) == YES

        def no(field):
            return form_data.get(field) == NO

        self.update(
            {
                "value": to_amount(val("property_value")),
                "mortgage_left": to_amount(val("mortgage_remaining")),
                "share": 100 if no("other_shareholders") else None,
                "disputed": val("in_dispute"),
                "rent": MoneyInterval(mi("rent_amount", val))
                if yes("is_rented")
                else MoneyInterval(0),
                "main": val("is_main_home"),
            }
        )


class PropertiesPayload(dict):
    def __init__(self, form_data={}):
        super(PropertiesPayload, self).__init__()

        # Extract the list of properties from the form data
        property_list = form_data.get("properties", [])

        # Convert each property dictionary to a PropertyPayload
        properties = [PropertyPayload(property_data) for property_data in property_list]

        # Calculate total mortgage payments and rent amounts
        total_mortgage = sum(
            float(property_data.get("mortgage_payments", 0))
            for property_data in property_list
        )
        total_rent = (
            sum(
                float(
                    MoneyInterval(property_data.get("rent_amount", {}))
                    .per_month()
                    .get("per_interval_value", 0)
                )
                for property_data in property_list
            )
            / 100
        )

        # Update the payload with the calculated data
        self.update(
            {
                "property_set": properties,
                "you": {
                    "income": {
                        "other_income": {
                            "per_interval_value": total_rent,
                            "interval_period": "per_month",
                        }
                    },
                    "deductions": {
                        "mortgage": {
                            "per_interval_value": total_mortgage,
                            "interval_period": "per_month",
                        }
                    },
                },
            },
        )


class MeansTest(View):
    forms = {
        "about-you": AboutYouForm,
        "benefits": BenefitsForm,
        "property": MultiplePropertiesForm,
    }

    def __init__(self, current_form_class, current_name):
        self.form_class = current_form_class
        self.current_name = current_name

    def dispatch_request(self):
        form = self.form_class()

        if isinstance(form, MultiplePropertiesForm):
            # Handle adding a property
            if "add-property" in request.form:
                form.properties.append_entry()
                form._submitted = False
                return render_template(self.form_class.template, form=form)

            # Handle removing a property
            elif (
                "remove-property-2" in request.form
                or "remove-property-3" in request.form
            ):
                form.properties.pop_entry()
                form._submitted = False
                return render_template(self.form_class.template, form=form)

        if form.validate_on_submit():
            session.get_eligibility().add(self.current_name, form.data)
            next_page = url_for(f"means_test.{self.get_next_page(self.current_name)}")
            payload = self.get_payload(session.get_eligibility())
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
        benefits_form = eligibility_data.forms.get("benefits", {})
        property_form = eligibility_data.forms.get("property", {})

        benefits = benefits_form.get("benefits", [])

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

        # Add in the property payload
        if eligibility_data.forms.get("about-you", {}).get("own_property"):
            payload["property_set"] = property_payload["property_set"]
            payload["you"]["income"]["other_income"]["per_interval_value"] = (
                property_payload["you"]["income"]["other_income"]["per_interval_value"]
            )
            payload["you"]["income"]["other_income"]["interval_period"] = (
                property_payload["you"]["income"]["other_income"]["interval_period"]
            )
            payload["you"]["deductions"]["mortgage"]["per_interval_value"] = (
                property_payload["you"]["deductions"]["mortgage"]["per_interval_value"]
            )
            payload["you"]["deductions"]["mortgage"]["interval_period"] = (
                property_payload["you"]["deductions"]["mortgage"]["interval_period"]
            )
        return payload


class CheckYourAnswers(MethodView):
    def get(self):
        return render_template("means_test/review.html", data=session.get_eligibility())
