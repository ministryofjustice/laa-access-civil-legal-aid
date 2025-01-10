from flask_wtf import FlaskForm
from wtforms.fields import RadioField, IntegerField
from govuk_frontend_wtf.wtforms_widgets import GovTextInput, GovSubmitInput
from wtforms.fields.simple import SubmitField
from wtforms.validators import InputRequired, NumberRange

from app.means_test.validators import ValidateIf
from app.means_test.widgets import MeansTestRadioInput
from flask_babel import gettext as _


class AboutYouForm(FlaskForm):
    title = "About you"

    partner = RadioField(
        "Do you have a partner?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        description="Your husband, wife, civil partner (unless you have permanently separated) or someone you live with as if you're married",
        validators=[InputRequired(message=_("Tell us whether you have a partner"))],
    )

    are_you_in_a_dispute = RadioField(
        "Are you in a dispute with your partner?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        validators=[
            ValidateIf("partner", "yes"),
            InputRequired(
                message=_("Tell us whether you’re in dispute with your partner")
            ),
        ],
    )

    on_benefits = RadioField(
        "Do you receive any benefits (including Child Benefit)?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        description="Being on some benefits can help you qualify for legal aid",
        validators=[InputRequired(message=_("Tell us whether you receive benefits"))],
    )

    have_children = RadioField(
        "Do you have any children aged 15 or under?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        description="Don't include any children who don't live with you",
        validators=[
            InputRequired(
                message=_("Tell us whether you have any children aged 15 or under")
            )
        ],
    )

    num_children = IntegerField(
        "How many?",
        widget=GovTextInput(),
        validators=[
            ValidateIf("have_children", "yes"),
            InputRequired(
                message=_("Tell us how many children you have aged 15 or under")
            ),
            NumberRange(min=1, max=50, message=_("Enter a number between 1 and 50")),
        ],
    )

    have_dependents = RadioField(
        "Do you have any dependants aged 16 or over?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        description="People who you live with and support financially. This could be a young person for whom you get Child Benefit",
        validators=[
            InputRequired(
                message=_("Tell us whether you have any dependants aged 16 or over")
            )
        ],
    )

    num_dependents = IntegerField(
        "How many?",
        widget=GovTextInput(),
        validators=[
            ValidateIf("have_dependents", "yes"),
            InputRequired(_("Tell us how many dependants you have aged 16 or over")),
            NumberRange(min=1, max=50, message=_("Enter a number between 1 and 50")),
        ],
    )

    own_property = RadioField(
        "Do you own any property?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        description="For example, a house, static caravan or flat",
        validators=[InputRequired(message=_("Tell us if you own any properties"))],
    )

    is_employed = RadioField(
        "Are you employed?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        description="This means working as an employee - you may be both employed and self-employed",
        validators=[InputRequired(message=_("Tell us if you are employed"))],
    )

    is_self_employed = RadioField(
        "Are you self-employed?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        description="This means working for yourself - you may be both employed and self-employed",
        validators=[InputRequired(message=_("Tell us if you are self-employed"))],
    )

    aged_60_or_over = RadioField(
        "Are you or your partner (if you have one) aged 60 or over?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        validators=[
            InputRequired(
                message=_("Tell us if you or your partner are aged 60 or over")
            )
        ],
    )

    have_savings = RadioField(
        "Do you have any savings or investments?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        validators=[
            InputRequired(message=_("Tell us whether you have savings or investments"))
        ],
    )

    have_valuables = RadioField(
        "Do you have any valuable items worth over £500 each?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        validators=[
            InputRequired(
                message=_("Tell us if you have any valuable items worth over £500 each")
            )
        ],
    )

    submit = SubmitField(_("Continue"), widget=GovSubmitInput())
