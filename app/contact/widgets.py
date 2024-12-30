from govuk_frontend_wtf.wtforms_widgets import GovCheckboxesInput
from app.categories.widgets import CategoryInputField


class RFCCheckboxInput(CategoryInputField, GovCheckboxesInput):
    pass
