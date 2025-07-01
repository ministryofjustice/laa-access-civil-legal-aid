from flask_babel import lazy_gettext as _

CONTACT_PREFERENCE = [
    ("call", _("I will call Civil Legal Advice")),
    ("callback", _("Call me back")),
    ("thirdparty", _("Call someone else instead of me")),
]
