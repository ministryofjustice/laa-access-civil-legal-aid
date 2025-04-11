from copy import deepcopy
from flask import session
from app.means_test.money_interval import MoneyInterval, to_amount


def recursive_update(orig, other):
    for key, val in other.items():
        if key not in orig:
            if isinstance(val, dict):
                orig[key] = deepcopy(val)
            else:
                orig[key] = val

        elif orig[key] == val:
            continue

        elif key == "notes" and orig[key] != val:
            orig[key] = "{0}\n\n{1}".format(orig[key], val)

        elif isinstance(val, dict):
            if MoneyInterval.is_money_interval(val):
                orig[key] = MoneyInterval(val)
            elif val != {}:
                if not isinstance(orig[key], dict):
                    orig[key] = {}
                orig[key] = recursive_update(orig[key], val)
        else:
            orig[key] = val

    return orig


class AboutYouPayload(dict):
    def __init__(self, form_data=None):
        super(AboutYouPayload, self).__init__()

        if form_data is None:
            form_data = {}

        def yes(field):
            return form_data.get(field, False) is True

        def val(field):
            return form_data.get(field)

        payload = {
            "dependants_young": val("num_children") if yes("has_children") else 0,
            "dependants_old": val("num_dependants") if yes("has_dependants") else 0,
            "is_you_or_your_partner_over_60": yes("aged_60_or_over"),
            "has_partner": yes("has_partner") and not yes("in_dispute"),
            "you": {"income": {"self_employed": yes("is_self_employed")}},
        }

        if (
            yes("has_partner")
            and not yes("in_dispute")
            and yes("partner_is_self_employed")
        ):
            payload["partner"] = {
                "income": {"self_employed": yes("partner_is_self_employed")}
            }

        if yes("own_property"):
            payload = recursive_update(payload, PropertiesPayload())
        else:
            payload = recursive_update(payload, PropertiesPayload.default())

        if yes("has_savings") or yes("has_valuables"):
            payload = recursive_update(payload, SavingsPayload())
        else:
            payload = recursive_update(payload, SavingsPayload.default())

        if not yes("on_benefits"):
            payload = recursive_update(payload, YourBenefitsPayload.default())

        payload = recursive_update(payload, IncomePayload())
        payload = recursive_update(payload, OutgoingsPayload())

        self.update(payload)


class YourBenefitsPayload(dict):
    @classmethod
    def default(cls):
        return {"specific_benefits": {}, "on_passported_benefits": False}

    def __init__(self, form_data=None):
        super(YourBenefitsPayload, self).__init__()

        if form_data is None:
            form_data = {}

        is_passported = session.get_eligibility().has_passported_benefits

        benefits = {}

        if session.get_eligibility().on_benefits:
            benefits = {
                "pension_credit": "pension_credit" in form_data.get("benefits", []),
                "job_seekers_allowance": "job_seekers_allowance"
                in form_data.get("benefits", []),
                "employment_support": "employment_support"
                in form_data.get("benefits", []),
                "universal_credit": "universal_credit" in form_data.get("benefits", []),
                "income_support": "income_support" in form_data.get("benefits", []),
            }

        payload = {
            "specific_benefits": benefits,
            "on_passported_benefits": is_passported,
        }

        if is_passported:
            payload = recursive_update(payload, IncomePayload.default())
            payload = recursive_update(payload, OutgoingsPayload.default())
        else:

            def val(field):
                return form_data.get(field)

            payload["you"] = {
                "income": {"child_benefits": MoneyInterval(val("child_benefits"))}
            }

        self.update(payload)


class AdditionalBenefitsPayload(dict):
    def __init__(self, form_data=None):
        super(AdditionalBenefitsPayload, self).__init__()

        if form_data is None:
            form_data = {}

        def val(field):
            return form_data.get(field)

        def yes(field):
            return form_data[field] is True

        benefits = val("benefits")

        payload = {
            "on_nass_benefits": False,
            "you": {
                "income": {
                    "benefits": MoneyInterval(val("total_other_benefit"))
                    if yes("other_benefits")
                    else MoneyInterval(0)
                }
            },
        }

        if benefits:
            payload["notes"] = "Other benefits:\n - {0}".format("\n - ".join(benefits))

        self.update(payload)


class PropertyPayload(dict):
    def __init__(self, form_data={}):
        super(PropertyPayload, self).__init__()

        def val(field):
            return form_data.get(field)

        def yes(field):
            return form_data.get(field) is True

        def no(field):
            return form_data.get(field) is False

        self.update(
            {
                "value": to_amount(val("property_value")),
                "mortgage_left": to_amount(val("mortgage_remaining")),
                "share": 100 if no("other_shareholders") else None,
                "disputed": val("in_dispute"),
                "rent": MoneyInterval(val("rent_amount"))
                if yes("is_rented")
                else MoneyInterval(0),
                "main": val("is_main_home"),
            }
        )


class PropertiesPayload(dict):
    @classmethod
    def default(cls):
        return {
            "property_set": [],
            "you": {
                "deductions": {"mortgage": MoneyInterval(0)},
                "income": {"other_income": MoneyInterval(0)},
            },
        }

    def __init__(self, form_data=None):
        super(PropertiesPayload, self).__init__()

        if form_data is None:
            form_data = {}

        properties = []

        if session.get_eligibility().owns_property:
            for property in form_data.get("properties", []):
                properties.append(PropertyPayload(property))

        if len(properties) == 0 and session.get_eligibility().owns_property:
            properties.append(PropertyPayload())

        def mortgage(index):
            return MoneyInterval(
                form_data.get("properties-%d-mortgage_payments" % index, 0)
            )

        total_mortgage = sum(map(mortgage, range(len(properties))))

        total_rent = sum(p["rent"] for p in properties)

        self.update(
            {
                "property_set": properties,
                "you": {
                    "income": {"other_income": total_rent},
                    "deductions": {"mortgage": total_mortgage},
                },
            }
        )


class SavingsPayload(dict):
    @classmethod
    def default(cls):
        return {
            "you": {
                "savings": {
                    "bank_balance": 0,
                    "investment_balance": 0,
                    "asset_balance": 0,
                }
            }
        }

    def __init__(self, form_data=None):
        super(SavingsPayload, self).__init__()

        if form_data is None:
            form_data = {}

        def val(field):
            return form_data.get(field)

        savings = 0
        investments = 0
        valuables = 0

        if session.get_eligibility().has_savings:
            savings = val("savings")
            investments = val("investments")
        if session.get_eligibility().has_valuables:
            valuables = val("valuables")

        self.update(
            {
                "you": {
                    "savings": {
                        "bank_balance": to_amount(savings),
                        "investment_balance": to_amount(investments),
                        "asset_balance": to_amount(valuables),
                    }
                }
            }
        )


class IncomePayload(dict):
    @staticmethod
    def income():
        return {
            "income": {
                "earnings": MoneyInterval(0),
                "tax_credits": MoneyInterval(0),
                "other_income": MoneyInterval(0),
                "self_employment_drawings": MoneyInterval(0),
                "maintenance_received": MoneyInterval(0),
                "pension": MoneyInterval(0),
            },
            "deductions": {
                "income_tax": MoneyInterval(0),
                "national_insurance": MoneyInterval(0),
            },
        }

    @classmethod
    def default(self):
        return {"you": self.income(), "partner": self.income()}

    def __init__(self, form_data=None):
        super(IncomePayload, self).__init__()

        if form_data is None:
            form_data = {}

        def income(person: str, self_employed=False, employed=False):
            def val(field):
                if person == "partner":
                    return form_data.get(f"partner_{field}")
                return form_data.get(field)

            child_tax_credit = (
                MoneyInterval(val("child_tax_credit"))
                if person == "you"
                else MoneyInterval(0)
            )
            payload = {
                person: {
                    "income": {
                        "earnings": MoneyInterval(val("earnings")),
                        "self_employment_drawings": MoneyInterval(0),
                        "tax_credits": MoneyInterval(val("working_tax_credit"))
                        + child_tax_credit,
                        "maintenance_received": MoneyInterval(
                            val("maintenance_received")
                        ),
                        "pension": MoneyInterval(val("pension")),
                        "other_income": MoneyInterval(val("other_income")),
                    },
                    "deductions": {
                        "income_tax": MoneyInterval(val("income_tax")),
                        "national_insurance": MoneyInterval(val("national_insurance")),
                    },
                }
            }

            if self_employed:
                payload[person]["income"]["earnings"] = MoneyInterval(0)
                payload[person]["income"]["self_employment_drawings"] = MoneyInterval(
                    val("earnings")
                )

            if not employed:
                payload[person]["income"]["earnings"] = MoneyInterval(0)
                payload[person]["income"]["self_employment_drawings"] = MoneyInterval(0)
                payload[person]["income"]["tax_credits"] = MoneyInterval(0)
                payload[person]["deductions"]["income_tax"] = MoneyInterval(0)
                payload[person]["deductions"]["national_insurance"] = MoneyInterval(0)

            return payload

        self_employed = (
            session.get_eligibility().is_self_employed
            and not session.get_eligibility().is_employed
        )
        employed = (
            session.get_eligibility().is_self_employed
            or session.get_eligibility().is_employed
        )
        partner_self_employed = (
            session.get_eligibility().is_partner_self_employed
            and not session.get_eligibility().is_partner_employed
        )
        partner_employed = (
            session.get_eligibility().is_partner_self_employed
            or session.get_eligibility().is_partner_employed
        )

        payload = income(
            person="you",
            self_employed=self_employed,
            employed=employed,
        )

        if session.get_eligibility().owns_property:
            rents = [
                MoneyInterval(p["rent_amount"])
                for p in session.get_eligibility()
                .forms.get("property", {})
                .get("properties", [])
            ]
            total_rent = sum(rents)
            payload["you"]["income"]["other_income"] += total_rent

        if session.get_eligibility().has_partner:
            partner_payload = income(
                person="partner",
                self_employed=partner_self_employed,
                employed=partner_employed,
            )
            payload = recursive_update(payload, partner_payload)

        self.update(payload)


class OutgoingsPayload(dict):
    @classmethod
    def default(cls):
        return {
            "you": {
                "deductions": {
                    "rent": MoneyInterval(0),
                    "maintenance": MoneyInterval(0),
                    "childcare": MoneyInterval(0),
                    "criminal_legalaid_contributions": 0,
                }
            }
        }

    def __init__(self, form_data=None):
        super(OutgoingsPayload, self).__init__()

        if form_data is None:
            form_data = {}

        def val(field):
            return form_data.get(field)

        self.update(
            {
                "you": {
                    "deductions": {
                        "rent": MoneyInterval(val("rent")),
                        "maintenance": MoneyInterval(val("maintenance")),
                        "criminal_legalaid_contributions": to_amount(
                            val("income_contribution")
                        ),
                        "childcare": MoneyInterval(val("childcare")),
                    }
                }
            }
        )
        if (
            not session.get_eligibility().has_children
            and not session.get_eligibility().has_dependants
        ):
            self["you"]["deductions"]["childcare"] = MoneyInterval(0)


class MeansTestPayload(dict):
    """
    Encapsulates the means test data and saving to and querying the API
    """

    def __init__(self, *args, **kwargs):
        super(MeansTestPayload, self).__init__(*args, **kwargs)

        self.reference = session.get("ec_reference", None)

        def zero_finances():
            return {
                "income": {
                    "earnings": MoneyInterval(0),
                    "benefits": MoneyInterval(0),
                    "tax_credits": MoneyInterval(0),
                    "child_benefits": MoneyInterval(0),
                    "other_income": MoneyInterval(0),
                    "self_employment_drawings": MoneyInterval(0),
                    "maintenance_received": MoneyInterval(0),
                    "pension": MoneyInterval(0),
                    "self_employed": False,
                },
                "savings": {
                    "credit_balance": 0,
                    "investment_balance": 0,
                    "asset_balance": 0,
                    "bank_balance": 0,
                },
                "deductions": {
                    "income_tax": MoneyInterval(0),
                    "mortgage": MoneyInterval(0),
                    "childcare": MoneyInterval(0),
                    "rent": MoneyInterval(0),
                    "maintenance": MoneyInterval(0),
                    "national_insurance": MoneyInterval(0),
                    "criminal_legalaid_contributions": 0,
                },
            }

        self.update(
            {
                "you": zero_finances(),
                "dependants_young": 0,
                "dependants_old": 0,
                "on_passported_benefits": False,
                "on_nass_benefits": False,
                "specific_benefits": {},
            }
        )

        if session.get_eligibility().has_partner:
            self.update({"partner": zero_finances()})

        if session.category:
            self["category"] = session.category.chs_code

    def update(self, other=None, **kwargs):
        """
        Recursively merge dicts into self
        """
        if other is None:
            other = {}
        other.update(kwargs)
        recursive_update(self, other)

    def update_from_form(self, form_name, form_data):
        payload_class_mapping = {
            "about-you": AboutYouPayload,
            "benefits": YourBenefitsPayload,
            "additional-benefits": AdditionalBenefitsPayload,
            "property": PropertiesPayload,
            "savings": SavingsPayload,
            "income": IncomePayload,
            "outgoings": OutgoingsPayload,
        }
        payload_class = payload_class_mapping[form_name]
        self.update(payload_class(form_data))

    def update_from_session(self):
        for form_name, form_data in session.get_eligibility().forms.items():
            self.update_from_form(form_name, form_data)
