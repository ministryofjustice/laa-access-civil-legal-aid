from flask import session
from wtforms.fields import SelectMultipleField
from app.means_test.fields import YesNoField


class PartnerMixin(object):
    def __init__(self, *args, **kwargs):
        partner_label = kwargs.pop("partner_label", kwargs.get("label"))
        partner_description = kwargs.pop(
            "partner_description", kwargs.get("description")
        )
        if session.get_eligibility().has_partner:
            kwargs["label"] = partner_label
            kwargs["description"] = partner_description
        super(PartnerMixin, self).__init__(*args, **kwargs)


class PartnerMultiCheckboxField(PartnerMixin, SelectMultipleField):
    pass


class PartnerYesNoField(PartnerMixin, YesNoField):
    pass
