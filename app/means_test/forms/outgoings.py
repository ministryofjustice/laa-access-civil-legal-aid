from flask import session
from flask_babel import lazy_gettext as _
from app.means_test.forms import BaseMeansTestForm
from app.means_test.fields import MoneyIntervalField, MoneyIntervalWidget, MoneyField
from app.means_test.validators import MoneyIntervalAmountRequired, ValidateIfSession
from app.means_test.widgets import MoneyInput
from wtforms.validators import InputRequired, NumberRange
from wtforms import SubmitField
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput


class PartnerMoneyIntervalField(MoneyIntervalField):
    def __init__(self, *args, **kwargs):
        self._hint_text = kwargs.pop("hint_text", None)
        self._partner_hint_text = kwargs.pop("partner_hint_text", None)
        super().__init__(*args, **kwargs)

    @property
    def hint_text(self):
        return self._partner_hint_text if session.get_eligibility().has_partner else self._hint_text

    @hint_text.setter
    def hint_text(self, value):
        pass


class PartnerMoneyField(MoneyField):
    def __init__(self, label=None, description=None, partner_description=None, *args, **kwargs):
        self._description = description
        self._partner_description = partner_description

        kwargs.pop("description", None)

        super().__init__(label=label, **kwargs)

    @property
    def description(self):
        return self._partner_description if session.get_eligibility().has_partner else self._description

    @description.setter
    def description(self, value):
        pass


class OutgoingsForm(BaseMeansTestForm):
    title = _("Your outgoings")
    partner_title = _("You and your partner’s outgoings")

    template = "means_test/outgoings.html"

    @classmethod
    def should_show(cls) -> bool:
        return not session.get_eligibility().has_passported_benefits

    @property
    def has_children_dependants(self):
        return session.get_eligibility().is_eligible_for_child_benefits

    @property
    def has_partner(self):
        return session.get_eligibility().has_partner

    rent = PartnerMoneyIntervalField(
        _("Rent"),
        hint_text=_("Money you pay your landlord for rent. Do not include rent that is paid by Housing Benefit."),
        partner_hint_text=_(
            "Money you and your partner pay your landlord for rent, or enter 0 if you don’t pay rent. Do not include rent that is paid by Housing Benefit."
        ),
        widget=MoneyIntervalWidget(),
        validators=[
            MoneyIntervalAmountRequired(
                message=_("Tell us how much rent you pay"),
                freq_message=_("Tell us how often you pay this rent"),
                amount_message=_("Tell us how much rent you pay"),
            ),
        ],
        exclude_intervals=["per_2week", "per_4week"],
    )

    maintenance = PartnerMoneyIntervalField(
        _("Maintenance"),
        hint_text=_("Money you pay to an ex-partner for their living costs, or enter 0 if this doesn’t apply to you"),
        partner_hint_text=_(
            "Money you and/or your partner pay to an ex-partner for their living costs, or enter 0 if this doesn’t apply"
        ),
        widget=MoneyIntervalWidget(),
        validators=[
            MoneyIntervalAmountRequired(
                message=_("Tell us how much maintenance you pay"),
                freq_message=_("Tell us how often you pay this maintenance"),
                amount_message=_("Tell us how much maintenance you pay"),
            ),
        ],
        exclude_intervals=["per_2week"],
    )

    income_contribution = PartnerMoneyField(
        _("Monthly Income Contribution Order"),
        widget=MoneyInput(),
        description=_(
            "Money you pay per month towards your Criminal Legal Aid, or enter 0 if this doesn’t apply to you"
        ),
        partner_description=_(
            "Money you and/or your partner pay per month towards your Criminal Legal Aid, or enter 0 if this doesn’t apply"
        ),
        validators=[
            InputRequired(message=_("Tell us the approximate value of this property")),
            NumberRange(min=0, max=999999999, message=_("Enter a value of more than £0")),
        ],
    )

    childcare = PartnerMoneyIntervalField(
        _("Childcare"),
        hint_text=_("Money you pay for your child to be looked after while you work or study outside of your home"),
        partner_hint_text=_(
            "Money you and your partner pay for your child to be looked after while you work or study outside of your home"
        ),
        widget=MoneyIntervalWidget(),
        validators=[
            ValidateIfSession("is_eligible_for_child_benefits", True),
            MoneyIntervalAmountRequired(
                message=_("Tell us how much you pay towards childcare"),
                freq_message=_("Tell us how often you pay childcare costs"),
                amount_message=_("Tell us how much you pay towards childcare"),
            ),
        ],
        exclude_intervals=["per_2week", "per_4week"],
    )

    submit = SubmitField(_("Review your answers"), widget=GovSubmitInput())
