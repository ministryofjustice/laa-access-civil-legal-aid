from govuk_frontend_wtf.wtforms_widgets import (
    GovRadioInput,
    GovCheckboxesInput,
    GovTextInput,
)
from app.means_test.widgets import MeansTestInputField
from wtforms import SelectField


class ContactRadioInput(MeansTestInputField, GovRadioInput):
    pass


class ContactCheckboxInput(MeansTestInputField, GovCheckboxesInput):
    pass


class ContactSelectField(SelectField):
    def pre_validate(self, form):
        """Override to prevent WTForms' internal choice validation"""
        pass


class ContactTextInput(MeansTestInputField, GovTextInput):
    pass
