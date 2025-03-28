from wtforms import StringField, Form, HiddenField
from govuk_frontend_wtf.wtforms_widgets import GovTextInput
from wtforms.validators import InputRequired
from app.find_a_legal_adviser.validators import ValidRegionPostcode


class FindLegalAdviserForm(Form):
    postcode = StringField(
        "Enter postcode",
        validators=[InputRequired("Enter a postcode"), ValidRegionPostcode()],
        description="For example, SW1H 9AJ.",
        widget=GovTextInput(),
    )
    category = HiddenField()
    secondary_category = HiddenField()

    def __init__(self, formdata=None, **kwargs):
        super().__init__(formdata, **kwargs)
        self.postcode_region = None  # Initialize the storage for the postcode lookup result
