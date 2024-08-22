from flask_wtf import FlaskForm
from flask import url_for, session
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

    @property
    def valid_choices(self):
        return {choice[0] for choice in self.question.choices}

    def get_description_from_key(self, input):
        for key, description in self.question.choices:
            if key == input:
                return description


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

    @property
    def valid_choices(self):
        return {choice[0] for choice in self.question.choices}

    def get_description_from_key(self, input):
        for key, description in self.question.choices:
            if key == input:
                return description


class Category:
    title = "Category of Law"


class DiscriminationQuestions:
    question_forms = [DiscriminationForm, DiscriminationWhyForm]

    def summary_form(self):
        form = [
            {
                "key": {"text": "Category"},
                "value": {"text": "Discrimination"},
                "actions": {
                    "items": [
                        {
                            "href": url_for("categories.index"),
                            "text": "Change",
                            "visuallyHiddenText": "Category",
                        }
                    ]
                },
            },
            {
                "key": {"text": self.question_forms[0]().title},
                "value": {
                    "text": self.question_forms[0]().get_description_from_key(
                        session["discrimination"]["where"]
                    )
                },
                "actions": {
                    "items": [
                        {
                            "href": url_for(
                                "categories.discrimination.index",
                                previous_answer=session["discrimination"]["where"],
                                change=True,
                            ),
                            "text": "Change",
                            "visuallyHiddenText": self.question_forms[0]().title,
                        }
                    ]
                },
            },
            {
                "key": {"text": self.question_forms[1]().title},
                "value": {
                    "text": self.question_forms[1]().get_description_from_key(
                        session["discrimination"]["why"]
                    )
                },
                "actions": {
                    "items": [
                        {
                            "href": url_for(
                                "categories.discrimination.protected_characteristics",
                                where=session["discrimination"]["where"],
                                previous_answer=session["discrimination"]["why"],
                                change=True,
                            ),
                            "text": "Change",
                            "visuallyHiddenText": self.question_forms[0]().title,
                        }
                    ]
                },
            },
        ]
        return form
