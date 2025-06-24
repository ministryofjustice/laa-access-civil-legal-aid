from wtforms import SelectMultipleField
from app.categories.validators import ExclusiveValue
from app.categories.widgets import CategoryCheckboxInput
from app.categories.forms import QuestionForm
from wtforms.validators import InputRequired
from app.categories.x_cat.forms import AreYouUnder18Form
from app.categories.constants import DISCRIMINATION
from flask_babel import lazy_gettext as _


class DiscriminationQuestionForm(QuestionForm):
    category = DISCRIMINATION


class DiscriminationWhereForm(DiscriminationQuestionForm):
    title = _("Where did the discrimination happen?")

    next_step_mapping = {
        "*": "categories.discrimination.why",
        "notsure": "categories.discrimination.why",
    }

    question = SelectMultipleField(
        title,
        widget=CategoryCheckboxInput(show_divider=True, hint_text=_("You can select more than one.")),
        validators=[InputRequired(message=_("Select where the discrimination happened"))],
        choices=[
            ("work", _("Work - including colleagues, employer or employment agency")),
            ("school", _("School, college, university or other education setting")),
            (
                "business",
                _("Businesses or services - such as a shop, restaurant, train, hotel, bank, law firm"),
            ),
            ("healthcare", _("Health or care - such as a hospital or care home")),
            ("housing", _("Housing - such as a landlord or estate agent")),
            (
                "public",
                _(
                    "Public services and authorities - such as the police, social services, council or local authority, jobcentre, government"
                ),
            ),
            ("club", _("Clubs and associations - such as a sports club")),
            ("", ""),
            ("notsure", _("I’m not sure")),
        ],
    )


class DiscriminationWhyForm(DiscriminationQuestionForm):
    depends_on = DiscriminationWhereForm
    title = _("Why were you discriminated against?")

    next_step_mapping = {
        "*": "categories.discrimination.age",
        "none": "categories.discrimination.cannot_find_your_problem",
    }

    question = SelectMultipleField(
        title,
        widget=CategoryCheckboxInput(
            show_divider=True,
            hint_text=_("You can select more than one."),
            behaviour="exclusive",
        ),
        validators=[
            InputRequired(message=_("Select why you were discriminated against")),
            ExclusiveValue(
                exclusive_value="none",
                message=_("Select why you were discriminated against, or select ‘None of these’"),
            ),
        ],
        choices=[
            ("race", _("Race, colour, ethnicity, nationality")),
            ("sex", _("Sex (male or female)")),
            ("disability", _("Disability, health condition, mental health condition")),
            ("religion", _("Religion, belief, lack of religion")),
            ("age", _("Age")),
            ("pregnancy", _("Pregnancy or being a mother")),
            (
                "sexualorientation",
                _("Sexual orientation - gay, bisexual, other sexuality"),
            ),
            (
                "gender",
                _("Gender reassignment, being transgender, non-binary or gender-fluid"),
            ),
            (
                "marriage",
                _("Married status - being married, in a civil partnership"),
            ),
            ("", ""),
            ("none", _("None of these")),
        ],
    )


class DiscriminationAreYouUnder18Form(AreYouUnder18Form):
    depends_on = DiscriminationWhyForm
    category = DISCRIMINATION

    next_step_mapping = {
        "yes": {"endpoint": "contact.contact_us_fast_tracked", "reason": "other"},
        "no": "categories.results.in_scope",
    }
