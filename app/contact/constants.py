from flask_babel import lazy_gettext as _

CONTACT_PREFERENCE = [
    ("call", _("I will call Civil Legal Advice")),
    ("callback", _("Call me back")),
    ("thirdparty", _("Call someone else instead of me")),
]

# If there are no slots available for call me back this will show
NO_SLOT_CONTACT_PREFERENCE = [
    ("call", _("I will call Civil Legal Advice")),
    ("thirdparty", _("I want Civil Legal Advice to call someone else instead of me")),
]
