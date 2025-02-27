from wtforms import SelectMultipleField
from app.categories.validators import ExclusiveValue
from app.categories.widgets import CategoryCheckboxInput
from app.categories.forms import QuestionForm
from wtforms.validators import InputRequired
from app.categories.x_cat.forms import AreYouUnder18Form
from app.categories.constants import DISCRIMINATION


class DiscriminationQuestionForm(QuestionForm):
    category = DISCRIMINATION


class DiscriminationWhereForm(DiscriminationQuestionForm):
    title = "Where did the discrimination happen?"

    next_step_mapping = {
        "*": "categories.discrimination.why",
        "notsure": "categories.discrimination.why",
    }

    question = SelectMultipleField(
        title,
        widget=CategoryCheckboxInput(
            show_divider=True, hint_text="You can select more than one."
        ),
        validators=[InputRequired(message="Select where the discrimination happened")],
        choices=[
            ("work", "Work - including colleagues, employer or employment agency"),
            ("school", "School, college, university or other education setting"),
            (
                "business",
                "Businesses or services - such as a shop, restaurant, train, hotel, bank, law firm",
            ),
            ("healthcare", "Health or care - such as a hospital or care home"),
            ("housing", "Housing - such as a landlord or estate agent"),
            (
                "public",
                "Public services and authorities - such as the police, social services, council or local authority, jobcentre, government",
            ),
            ("club", "Clubs and associations - such as a sports club"),
            ("", ""),
            ("notsure", "I’m not sure"),
        ],
    )


class DiscriminationWhyForm(DiscriminationQuestionForm):
    title = "Why were you discriminated against?"

    next_step_mapping = {
        "*": "categories.discrimination.age",
        "none": "categories.discrimination.cannot_find_your_problem",
    }

    question = SelectMultipleField(
        title,
        widget=CategoryCheckboxInput(
            show_divider=True,
            hint_text="You can select more than one.",
            behaviour="exclusive",
        ),
        validators=[
            InputRequired(message="Select why you were discriminated against"),
            ExclusiveValue(
                exclusive_value="none",
                message="Select why you were discriminated against, or select ‘None of these’",
            ),
        ],
        choices=[
            ("race", "Race, colour, ethnicity, nationality"),
            ("sex", "Sex (male or female)"),
            ("disability", "Disability, health condition, mental health condition"),
            ("religion", "Religion, belief, lack of religion"),
            ("age", "Age"),
            ("pregnancy", "Pregnancy or being a mother"),
            (
                "sexualorientation",
                "Sexual orientation - gay, bisexual, other sexuality",
            ),
            (
                "gender",
                "Gender reassignment, being transgender, non-binary or gender-fluid",
            ),
            (
                "marriage",
                "Married status - being married, in a civil partnership",
            ),
            ("", ""),
            ("none", "None of these"),
        ],
    )


class DiscriminationAreYouUnder18Form(AreYouUnder18Form):
    category = DISCRIMINATION

    next_step_mapping = {
        "yes": "contact.contact_us",
        "no": "categories.results.in_scope",
    }
