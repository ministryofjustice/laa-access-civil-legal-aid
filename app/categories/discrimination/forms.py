from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovRadioInput, GovSubmitInput
from wtforms import RadioField, SubmitField
from wtforms.validators import InputRequired


class DiscriminationForm(FlaskForm):
    category = "Discrimination"

    title = "Where did the discrimination happen?"

    question = RadioField(
        "",
        widget=GovRadioInput(),
        validators=[InputRequired(message="Select where the discrimination happened")],
        choices=[
            ("work", "Work - including colleagues, employer or employment agency"),
            ("education", "School, college, university or other education setting"),
            (
                "business",
                "Businesses or service provision - like a shop, restaurant, train, hotel, bank, law firm",
            ),
            ("health", "Health or care - like a hospital or care home"),
            ("housing", "Housing provision - like a landlord or estate agent"),
            (
                "public_services",
                "Public services and authorities - like the police, social services, council or local authority, jobcentre, government",
            ),
            ("clubs", "Clubs and associations - like a sports club"),
            ("", ""),
            ("other", "Not sure"),
        ],
    )

    submit = SubmitField("Continue", widget=GovSubmitInput())


class DiscriminationWhyForm(FlaskForm):
    category = "Discrimination"

    title = "Why were you treated differently?"

    question = RadioField(
        "",
        widget=GovRadioInput(),
        validators=[InputRequired(message="Why were you treated differently")],
        choices=[
            ("race", "Race, colour of skin, ethnicity"),
            ("sex", "Sex (male or female)"),
            ("disability", "Disability, health condition, mental health condition"),
            ("religion", "Religion, belief, lack of religion"),
            ("age", "Age"),
            ("sexual-orientation", "Sexual orientation - gay, bi, other sexuality"),
            ("gender", "Gender - trans, gender reassignment, other gender issue"),
            ("pregnancy", "Pregnancy or being a mother"),
            (
                "marriage",
                "Married status - being married, in a civil partnership, unmarried",
            ),
            ("", ""),
            ("other", "None of the above"),
        ],
    )

    submit = SubmitField("Continue", widget=GovSubmitInput())
