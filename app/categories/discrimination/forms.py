from wtforms import RadioField
from app.categories.widgets import CategoryRadioInput
from app.categories.forms import QuestionForm
from wtforms.validators import InputRequired


class DiscriminationQuestionForm(QuestionForm):
    category = "Discrimination"


class DiscriminationWhereForm(DiscriminationQuestionForm):
    title = "Where did the discrimination happen?"

    next_step_mapping = {
        "work": "categories.discrimination.why",
        "school": "categories.discrimination.why",
        "business": "categories.discrimination.why",
        "healthcare": "categories.discrimination.why",
        "housing": "categories.discrimination.why",
        "public": "categories.discrimination.why",
        "club": "categories.discrimination.why",
        "notsure": "categories.alternative_help",
    }

    question = RadioField(
        title,
        widget=CategoryRadioInput(show_divider=True),
        validators=[InputRequired(message="Select where the discrimination happened")],
        choices=[
            ("work", "Work - including colleagues, employer or employment agency"),
            ("school", "School, college, university or other education settings"),
            (
                "business",
                "Businesses or service provision - like a shop, restaurant, train, hotel, bank, law firm",
            ),
            ("healthcare", "Health or care - like a hospital or care home"),
            ("housing", "Housing provision - like a landlord or estate agent"),
            (
                "public",
                "Public services and authorities - like the police, social services, council or local authority, jobcentre, government",
            ),
            ("club", "Clubs and associations - like a sports club"),
            ("", ""),
            ("notsure", "Not sure"),
        ],
    )

    show_or_divisor = True

class DiscriminationWhyForm(DiscriminationQuestionForm):
    title = "Why were you treated differently?"

    next_step_mapping = {
        "race": "categories.results.in_scope",
        "sex": "categories.results.in_scope",
        "disability": "categories.results.in_scope",
        "religion": "categories.results.in_scope",
        "age": "categories.results.in_scope",
        "sexualorientation": "categories.results.in_scope",
        "gender": "categories.results.in_scope",
        "pregnancy": "categories.results.in_scope",
        "none": "categories.results.alternative_help",
    }

    question = RadioField(
        title,
        widget=CategoryRadioInput(show_divider=True),
        validators=[InputRequired(message="Select why you were treated differently")],
        choices=[
            ("race", "Race, colour of skin, ethnicity"),
            ("sex", "Sex (male or female)"),
            ("disability", "Disability, health condition, mental health condition"),
            ("religion", "Religion, belief, lack of religion"),
            ("age", "Age"),
            ("sexualorientation", "Sexual orientation - gay, bi, other sexuality"),
            ("gender", "Gender - trans, gender reassignment, other gender issue"),
            ("pregnancy", "Pregnancy or being a mother"),
            (
                "marriage",
                "Married status - being married, in a civil partnership, unmarried",
            ),
            ("", ""),
            ("none", "None of the above"),
        ],
    )

    show_or_divisor = True
