from app.categories.forms import QuestionForm
from wtforms import RadioField

from app.categories.redirect import CheckRedirect, CheckDestination
from app.categories.widgets import CategoryRadioInput
from wtforms.validators import InputRequired


class DiscriminationWhyForm(QuestionForm):
    category = "Discrimination"

    title = "Why were you treated differently?"

    routing_logic = {
        "disability": CheckRedirect(destination=CheckDestination.MEANS_TEST)
    }

    question = RadioField(
        title,
        widget=CategoryRadioInput(),
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


class DiscriminationWhereForm(QuestionForm):
    category = "Discrimination"

    title = "Where did the discrimination happen?"

    routing_logic = {"work": DiscriminationWhyForm}

    question = RadioField(
        title,
        widget=CategoryRadioInput(),
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
