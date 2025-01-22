from flask import session
from wtforms.fields import RadioField, IntegerField
from wtforms.fields.core import Label
from govuk_frontend_wtf.wtforms_widgets import GovTextInput
from wtforms.validators import InputRequired, NumberRange
from app.means_test.widgets import MeansTestRadioInput
from flask_babel import gettext as _
from app.means_test import YES, NO
from app.means_test.forms import BaseMeansTestForm
from app.means_test.fields import MoneyIntervalField, MoneyIntervalFieldWidget
from app.means_test.validators import MoneyIntervalAmountRequired
from app.means_test.validators import ValidateIf


class PartnerRadioField(RadioField):
    def __init__(self, label, partner_label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._label = label
        self._partner_label = partner_label

    @property
    def label(self):
        if session.get_eligibility().has_partner:
            return Label(self.name, self._partner_label)
        else:
            return Label(self.name, self._label)

    @label.setter
    def label(self, value):
        pass


class PropertyForm(BaseMeansTestForm):
    @property
    def title(self):
        if session.get_eligibility().has_partner:
            return _("You and your partner’s property")
        else:
            return _("Your property")

    template = "means_test/property.html"

    @property
    def has_partner(self):
        return session.get_eligibility().has_partner

    @classmethod
    def should_show(cls) -> bool:
        return (
            session.get_eligibility().forms.get("about-you", {}).get("own_property")
            == YES
        )

    is_main_home = RadioField(
        "Is this property your main home?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        description="If you’re temporarily living away from the property, select ‘Yes’",
        validators=[InputRequired(message=_("Tell us whether this is your main home"))],
    )

    other_shareholders = PartnerRadioField(
        partner_label=_(
            "Does anyone else (other than you or your partner) own a share of the property?"
        ),
        label=_("Does anyone else own a share of the property?"),
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        description="Select ‘Yes’ if you share ownership with a friend, relative or ex-partner",
        validators=[
            InputRequired(
                message=_("Tell us whether anyone else owns a share of this property")
            )
        ],
    )

    property_value = IntegerField(
        "How much is the property worth?",
        widget=GovTextInput(),
        description="Use a property website or the Land Registry house prices website.",
        validators=[
            InputRequired(message=_("Tell us the approximate value of this property")),
            NumberRange(
                min=0, max=999999999, message=_("Enter a value of more than £0")
            ),
        ],
    )

    mortgage_remaining = IntegerField(
        "How much is left to pay on the mortgage?",
        widget=GovTextInput(),
        description="Include the full amount owed, even if the property has shared ownership, or enter 0 if you have no mortgage",
        validators=[
            InputRequired(message=_("Tell us how much is left to pay on the mortgage")),
            NumberRange(
                min=0, max=999999999, message=_("Enter a value of more than £0")
            ),
        ],
    )

    mortgage_payments = IntegerField(
        "How much was your monthly mortgage repayment last month?",
        widget=GovTextInput(),
        validators=[
            InputRequired(message=_("Enter your mortgage repayment for last month")),
            NumberRange(
                min=0, max=999999999, message=_("Enter a value of more than £0")
            ),
        ],
    )

    is_rented = RadioField(
        _("Do you rent out any part of this property?"),
        choices=[(YES, _("Yes")), (NO, _("No"))],
        widget=MeansTestRadioInput(),
        validators=[
            InputRequired(
                message=_("Tell us whether you rent out some of this property")
            )
        ],
    )

    rent_amount = MoneyIntervalField(
        _("If Yes, how much rent did you receive last month?"),
        hint_text=_("For example, £32.18 per week"),
        widget=MoneyIntervalFieldWidget(),
        validators=[
            ValidateIf("is_rented", YES),
            MoneyIntervalAmountRequired(
                message=_("Tell us how much rent you receive from this property"),
                freq_message=_("Tell us how often you receive this rent"),
                amount_message=_("Tell us how much rent you receive each week"),
            ),
        ],
    )

    in_dispute = RadioField(
        "Is your share of the property in dispute?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        description="For example, as part of the financial settlement of a divorce",
        validators=[
            InputRequired(message=_("Tell us whether this property is in dispute"))
        ],
    )
