from wtforms import Form
from wtforms import SelectMultipleField
from app.contact.widgets import RFCCheckboxInput


class ContactQuestionForm(Form):
    next_step_mapping = {
        "notsure": "contact",
    }

    question = SelectMultipleField(
        widget=RFCCheckboxInput(show_divider=True, hint_text="Select all that apply"),
        choices=[
            ("CANT_ANSWER", "I don’t know how to answer a question"),
            ("MISSING_PAPERWORK", "I don’t have the paperwork I need"),
            (
                "PREFER_SPEAKING",
                "I’d prefer to speak to someone",
            ),
            ("DIFFICULTY_ONLINE", "I have trouble using online services"),
            ("HOW_SERVICE_HELPS", "I don’t understand how this service can help me"),
            (
                "AREA_NOT_COVERED",
                "My problem area isn’t covered",
            ),
            ("PNS", "I’d prefer not to say"),
            ("OTHER", "Another reason"),
        ],
    )
