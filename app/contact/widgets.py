from govuk_frontend_wtf.wtforms_widgets import GovRadioInput
from app.means_test.widgets import MeansTestInputField


class ContactRadioInput(MeansTestInputField, GovRadioInput):
    pass
