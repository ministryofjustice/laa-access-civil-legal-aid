from flask import session
from flask_babel import lazy_gettext as _
from app.means_test.forms import BaseMeansTestForm
from app.means_test.fields import MoneyIntervalField, MoneyIntervalWidget
from app.means_test.validators import MoneyIntervalAmountRequired


class PartnerMoneyIntervalField(MoneyIntervalField):
    def __init__(self, *args, **kwargs):
        self._hint_text = kwargs.pop("hint_text", None)
        self._partner_hint_text = kwargs.pop("partner_hint_text", None)
        super().__init__(*args, **kwargs)

    @property
    def hint_text(self):
        return (
            self._partner_hint_text
            if session.get_eligibility().has_partner
            else self._hint_text
        )

    @hint_text.setter
    def hint_text(self, value):
        pass


class OutgoingsForm(BaseMeansTestForm):
    title = _("Your outgoings")
    partner_title = _("You and your partner’s outgoings")

    template = "means_test/outgoings.html"

    @classmethod
    def should_show(cls) -> bool:
        return not session.get("eligibility").has_passported_benefits

    @property
    def has_partner(self):
        return session.get_eligibility().has_partner

    rent = PartnerMoneyIntervalField(
        _("Rent"),
        hint_text=_(
            "Money you pay your landlord for rent. Do not include rent that is paid by Housing Benefit."
        ),
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
        hint_text=_(
            "Money you pay to an ex-partner for their living costs, or enter 0 if this doesn’t apply to you"
        ),
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
        exclude_intervals=["per_4week"],
    )
