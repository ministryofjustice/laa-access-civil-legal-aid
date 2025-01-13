from flask_wtf import FlaskForm
from wtforms.fields import RadioField, IntegerField
from govuk_frontend_wtf.wtforms_widgets import GovTextInput, GovSubmitInput
from wtforms.fields.simple import SubmitField
from wtforms.validators import InputRequired, NumberRange

from app.means_test.validators import ValidateIf
from app.means_test.widgets import MeansTestRadioInput
from flask_babel import gettext as _

YES = "1"
NO = "0"


class AboutYouForm(FlaskForm):
    title = "About you"

    has_partner = RadioField(
        "Do you have a partner?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        description="Your husband, wife, civil partner (unless you have permanently separated) or someone you live with as if you're married",
        validators=[InputRequired(message=_("Tell us whether you have a partner"))],
    )

    are_you_in_a_dispute = RadioField(
        "Are you in a dispute with your partner?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        validators=[
            ValidateIf("has_partner", YES),
            InputRequired(
                message=_("Tell us whether you’re in dispute with your partner")
            ),
        ],
    )

    on_benefits = RadioField(
        "Do you receive any benefits (including Child Benefit)?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        description="Being on some benefits can help you qualify for legal aid",
        validators=[InputRequired(message=_("Tell us whether you receive benefits"))],
    )

    have_children = RadioField(
        "Do you have any children aged 15 or under?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        description="Don't include any children who don't live with you",
        validators=[
            InputRequired(
                message=_("Tell us whether you have any children aged 15 or under")
            )
        ],
    )

    num_children = IntegerField(
        "How many?",
        widget=GovTextInput(),
        validators=[
            ValidateIf("have_children", YES),
            InputRequired(
                message=_("Tell us how many children you have aged 15 or under")
            ),
            NumberRange(min=1, max=50, message=_("Enter a number between 1 and 50")),
        ],
    )

    have_dependents = RadioField(
        "Do you have any dependants aged 16 or over?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        description="People who you live with and support financially. This could be a young person for whom you get Child Benefit",
        validators=[
            InputRequired(
                message=_("Tell us whether you have any dependants aged 16 or over")
            )
        ],
    )

    num_dependents = IntegerField(
        "How many?",
        widget=GovTextInput(),
        validators=[
            ValidateIf("have_dependents", YES),
            InputRequired(_("Tell us how many dependants you have aged 16 or over")),
            NumberRange(min=1, max=50, message=_("Enter a number between 1 and 50")),
        ],
    )

    own_property = RadioField(
        "Do you own any property?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        description="For example, a house, static caravan or flat",
        validators=[InputRequired(message=_("Tell us if you own any properties"))],
    )

    is_employed = RadioField(
        "Are you employed?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        description="This means working as an employee - you may be both employed and self-employed",
        validators=[InputRequired(message=_("Tell us if you are employed"))],
    )

    partner_is_employed = RadioField(
        _("Is your partner employed?"),
        description=_(
            "This means working as an employee - your partner may be both employed and self-employed"
        ),
        choices=[(YES, "Yes"), (NO, "No")],
        validators=[
            ValidateIf("are_you_in_a_dispute", NO),
            InputRequired(message=_("Tell us whether your partner is employed")),
        ],
        widget=MeansTestRadioInput(),
    )

    is_self_employed = RadioField(
        "Are you self-employed?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        description="This means working for yourself - you may be both employed and self-employed",
        validators=[InputRequired(message=_("Tell us if you are self-employed"))],
    )

    partner_is_self_employed = RadioField(
        _("Is your partner self-employed?"),
        description=_(
            "This means working for yourself - your partner may be both employed and self-employed"
        ),
        choices=[(YES, "Yes"), (NO, "No")],
        validators=[
            ValidateIf("are_you_in_a_dispute", NO),
            InputRequired(message=_("Tell us whether your partner is self-employed")),
        ],
        widget=MeansTestRadioInput(),
    )

    aged_60_or_over = RadioField(
        "Are you or your partner (if you have one) aged 60 or over?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        validators=[
            InputRequired(
                message=_("Tell us if you or your partner are aged 60 or over")
            )
        ],
    )

    have_savings = RadioField(
        "Do you have any savings or investments?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        validators=[
            InputRequired(message=_("Tell us whether you have savings or investments"))
        ],
    )

    have_valuables = RadioField(
        "Do you have any valuable items worth over £500 each?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        validators=[
            InputRequired(
                message=_("Tell us if you have any valuable items worth over £500 each")
            )
        ],
    )

    submit = SubmitField(_("Continue"), widget=GovSubmitInput())

    def payload_2(self):
        return {
            "on_passported_benefits": "0",
            "category": "u" "debt",
            "is_you_or_your_partner_over_60": "u" "0",
            "has_partner": "0",
            "property_set": [],
            "specific_benefits": {},
            "dependants_old": 0,
            "you": {
                "savings": {
                    "credit_balance": 0,
                    "investment_balance": 0,
                    "asset_balance": 0,
                    "bank_balance": 0,
                },
                "deductions": {
                    "income_tax": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                    "mortgage": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                    "childcare": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                    "rent": {
                        "per_interval_value": 0,
                        "interval_period": "u" "per_week",
                    },
                    "maintenance": {
                        "per_interval_value": 0,
                        "interval_period": "u" "per_week",
                    },
                    "criminal_legalaid_contributions": 0,
                    "national_insurance": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                },
                "income": {
                    "self_employment_drawings": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                    "benefits": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                    "maintenance_received": {
                        "per_interval_value": 0,
                        "interval_period": "u" "per_week",
                    },
                    "self_employed": "0",
                    "tax_credits": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                    "earnings": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                    "child_benefits": {
                        "per_interval_value": 0,
                        "interval_period": "per_month",
                    },
                    "other_income": {
                        "per_interval_value": 0,
                        "interval_period": "u" "per_week",
                    },
                    "pension": {
                        "per_interval_value": 0,
                        "interval_period": "u" "per_week",
                    },
                },
            },
            "dependants_young": 0,
            "on_nass_benefits": "0",
        }

    def payload(self):
        payload = {
            "has_partner": YES
            if self.has_partner.data == YES and not self.are_you_in_a_dispute.data == NO
            else NO,
            "is_you_or_your_partner_over_60": "1",
            "dependants_young": self.num_children.data
            if self.have_children.data == YES
            else 0,
            "dependants_old": self.num_dependents.data
            if self.have_dependents.data == YES
            else 0,
            "you": {"income": {"self_employed": self.is_self_employed.data}},
            # TEST DATA
            "property_set": [],
            "category": "debt",
            "on_passported_benefits": "0",
            "on_nass_benefits": "0",
            "specific_benefits": {},
        }

        payload["you"] = {
            "savings": {
                "credit_balance": 0,
                "investment_balance": 0,
                "asset_balance": 0,
                "bank_balance": 0,
            },
            "deductions": {
                "income_tax": {"per_interval_value": 0, "interval_period": "per_month"},
                "mortgage": {"per_interval_value": 0, "interval_period": "per_month"},
                "childcare": {"per_interval_value": 0, "interval_period": "per_month"},
                "rent": {"per_interval_value": 0, "interval_period": "per_week"},
                "maintenance": {"per_interval_value": 0, "interval_period": "per_week"},
                "criminal_legalaid_contributions": 0,
                "national_insurance": {
                    "per_interval_value": 0,
                    "interval_period": "per_month",
                },
            },
            "income": {
                "self_employment_drawings": {
                    "per_interval_value": 0,
                    "interval_period": "per_month",
                },
                "benefits": {"per_interval_value": 0, "interval_period": "per_month"},
                "maintenance_received": {
                    "per_interval_value": 0,
                    "interval_period": "per_week",
                },
                "self_employed": "0",
                "tax_credits": {
                    "per_interval_value": 0,
                    "interval_period": "per_month",
                },
                "earnings": {"per_interval_value": 0, "interval_period": "per_month"},
                "child_benefits": {
                    "per_interval_value": 0,
                    "interval_period": "per_month",
                },
                "other_income": {
                    "per_interval_value": 0,
                    "interval_period": "per_month",
                },
                "pension": {"per_interval_value": 0, "interval_period": "per_month"},
                "total": 0,
            },
        }

        if payload["has_partner"] and self.partner_is_self_employed.data == YES:
            payload["partner"] = {
                "income": {"self_employed": self.partner_is_self_employed.data}
            }

        if self.own_property.data:
            # TODO: Get property data
            pass

        if self.have_savings or self.have_valuables:
            # TODO: Get savings data
            pass

        if self.on_benefits.data:
            # TODO: Get benefits data
            pass

        # TODO: Get income and outgoing data

        return payload

    """
{
   "on_passported_benefits":"0",
   "category":"u""debt",
   "is_you_or_your_partner_over_60":"u""0",
   "has_partner":"0",
   "property_set":[
      
   ],
   "specific_benefits":{
      
   },
   "dependants_old":0,
   "you":{
      "savings":{
         "credit_balance":0,
         "investment_balance":0,
         "asset_balance":0,
         "bank_balance":0
      },
      "deductions":{
         "income_tax":{
            "per_interval_value":0,
            "interval_period":"per_month"
         },
         "mortgage":{
            "per_interval_value":0,
            "interval_period":"per_month"
         },
         "childcare":{
            "per_interval_value":0,
            "interval_period":"per_month"
         },
         "rent":{
            "per_interval_value":0,
            "interval_period":"u""per_week"
         },
         "maintenance":{
            "per_interval_value":0,
            "interval_period":"u""per_week"
         },
         "criminal_legalaid_contributions":0,
         "national_insurance":{
            "per_interval_value":0,
            "interval_period":"per_month"
         }
      },
      "income":{
         "self_employment_drawings":{
            "per_interval_value":0,
            "interval_period":"per_month"
         },
         "benefits":{
            "per_interval_value":0,
            "interval_period":"per_month"
         },
         "maintenance_received":{
            "per_interval_value":0,
            "interval_period":"u""per_week"
         },
         "self_employed":"0",
         "tax_credits":{
            "per_interval_value":0,
            "interval_period":"per_month"
         },
         "earnings":{
            "per_interval_value":0,
            "interval_period":"per_month"
         },
         "child_benefits":{
            "per_interval_value":0,
            "interval_period":"per_month"
         },
         "other_income":{
            "per_interval_value":0,
            "interval_period":"u""per_week"
         },
         "pension":{
            "per_interval_value":0,
            "interval_period":"u""per_week"
         }
      }
   },
   "dependants_young":0,
   "on_nass_benefits":"0"
}
    """
