from flask import session
from wtforms.fields import RadioField, IntegerField
from govuk_frontend_wtf.wtforms_widgets import GovTextInput
from wtforms.validators import InputRequired, NumberRange
from app.means_test.widgets import MeansTestRadioInput
from flask_babel import gettext as _
from app.means_test import YES
from app.means_test.forms import BaseMeansTestForm


class PropertyForm(BaseMeansTestForm):
    title = _("Your property")

    template = "means_test/property.html"

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

    other_shareholders = RadioField(
        "Does anyone else own a share of the property?",
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

    is_rented = RadioField(
        "Do you rent out any part of this property?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        validators=[
            InputRequired(
                message=_("Tell us whether you rent out some of this property")
            )
        ],
    )
    # Add expanded field

    in_dispute = RadioField(
        "Is your share of the property in dispute?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        description="For example, as part of the financial settlement of a divorce",
        validators=[
            InputRequired(message=_("Tell us whether this property is in dispute"))
        ],
    )
