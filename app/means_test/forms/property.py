from flask import session
from wtforms import ValidationError
from wtforms.fields import RadioField, IntegerField, FieldList, FormField
from wtforms.fields.core import Label
from govuk_frontend_wtf.wtforms_widgets import GovTextInput
from wtforms.validators import InputRequired, NumberRange
from app.means_test.widgets import MeansTestRadioInput
from flask_babel import lazy_gettext as _
from app.means_test import YES, NO
from app.means_test.forms import BaseMeansTestForm
from app.means_test.fields import MoneyIntervalField, MoneyIntervalWidget
from app.means_test.validators import MoneyIntervalAmountRequired
from app.means_test.validators import ValidateIf
from app.means_test.money_interval import MoneyInterval, to_amount


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
                "value": to_amount(val("property_value") * 100),
                "mortgage_left": to_amount(val("mortgage_remaining") * 100),
                "share": 100 if no("other_shareholders") else None,
                "disputed": val("in_dispute"),
                "rent": MoneyInterval(val("rent_amount"))
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
                    "income": {"other_income": MoneyInterval(total_rent, "per_month")}
                },
                "deductions": {"mortgage": MoneyInterval(total_mortgage, "per_month")},
            },
        )


def validate_single_main_home(form, field):
    properties = form.properties.data
    main_home_count = 0
    for property_data in properties:
        if property_data.get("is_main_home") == "True":
            main_home_count += 1

    if main_home_count > 1:
        raise ValidationError(_("You can only have 1 main property"))


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
    template = "means_test/property.html"

    @property
    def has_partner(self):
        return session.get_eligibility().has_partner

    is_main_home = RadioField(
        _("Is this property your main home?"),
        choices=[(True, _("Yes")), (False, _("No"))],
        widget=MeansTestRadioInput(),
        description=_(
            "If you’re temporarily living away from the property, select ‘Yes’"
        ),
        validators=[InputRequired(message=_("Tell us whether this is your main home"))],
    )

    other_shareholders = PartnerRadioField(
        partner_label=_(
            "Does anyone else (other than you or your partner) own a share of the property?"
        ),
        label=_("Does anyone else own a share of the property?"),
        choices=[(YES, _("Yes")), (NO, _("No"))],
        widget=MeansTestRadioInput(),
        description=_(
            "Select ‘Yes’ if you share ownership with a friend, relative or ex-partner"
        ),
        validators=[
            InputRequired(
                message=_("Tell us whether anyone else owns a share of this property")
            )
        ],
    )

    property_value = IntegerField(
        _("How much is the property worth?"),
        widget=GovTextInput(),
        description=_(
            "Use a property website or the Land Registry house prices website."
        ),
        validators=[
            InputRequired(message=_("Tell us the approximate value of this property")),
            NumberRange(
                min=0, max=999999999, message=_("Enter a value of more than £0")
            ),
        ],
    )

    mortgage_remaining = IntegerField(
        _("How much is left to pay on the mortgage?"),
        widget=GovTextInput(),
        description=_(
            "Include the full amount owed, even if the property has shared ownership, or enter 0 if you have no mortgage"
        ),
        validators=[
            InputRequired(message=_("Tell us how much is left to pay on the mortgage")),
            NumberRange(
                min=0, max=999999999, message=_("Enter a value of more than £0")
            ),
        ],
    )

    mortgage_payments = IntegerField(
        _("How much was your monthly mortgage repayment last month?"),
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
        exclude_intervals=["per_4week"],
        widget=MoneyIntervalWidget(),
        validators=[
            ValidateIf("is_rented", YES),
            MoneyIntervalAmountRequired(
                message=_("Tell us how much rent you receive from this property"),
                freq_message=_("Tell us how often you receive this rent"),
                amount_message=_("Tell us how much rent you receive"),
            ),
        ],
    )

    in_dispute = RadioField(
        _("Is your share of the property in dispute?"),
        choices=[(True, _("Yes")), (False, _("No"))],
        widget=MeansTestRadioInput(),
        description=_("For example, as part of the financial settlement of a divorce"),
        validators=[
            InputRequired(message=_("Tell us whether this property is in dispute"))
        ],
    )


class MultiplePropertiesForm(BaseMeansTestForm):
    title = _("Your property")
    partner_title = _("You and your partner’s property")

    @classmethod
    def should_show(cls) -> bool:
        return (
            session.get_eligibility().forms.get("about-you", {}).get("own_property")
            == YES
        )

    properties = FieldList(
        FormField(PropertyForm),  # Each entry is an instance of PropertyForm
        min_entries=1,  # At least one property form to start
        max_entries=3,  # Allow a maximum of three properties
        validators=[validate_single_main_home],
    )

    template = "means_test/property.html"

    def get_payload(
        self,
        has_property: bool | None = False,
    ) -> dict:
        """Returns the property payload for the user and the partner.
        If a field can not be found the default of MoneyField(0) will be used.
        """
        payload = PropertiesPayload(self)

        return payload
