from flask import session
from app.contact.constants import NO_SLOT_CONTACT_PREFERENCE, CONTACT_PREFERENCE
from app.contact.forms.choose_an_option import OptionForm


def test_option_form_adjusts_choices_for_no_slots(app):
    with app.test_request_context():
        session["_time_slots"] = []

        form = OptionForm()
        assert form.contact_type.choices == NO_SLOT_CONTACT_PREFERENCE


def test_option_form_keeps_choices_for_multiple_slots(app):
    with app.test_request_context():
        session["_time_slots"] = ["slot1", "slot2"]

        form = OptionForm()
        assert form.contact_type.choices == CONTACT_PREFERENCE
