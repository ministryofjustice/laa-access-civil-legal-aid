from wtforms.fields import RadioField, IntegerField
from govuk_frontend_wtf.wtforms_widgets import GovTextInput, GovSubmitInput
from wtforms.fields.simple import SubmitField
from wtforms.validators import InputRequired, NumberRange
from flask_wtf import FlaskForm
from app.means_test.validators import ValidateIf
from app.means_test.widgets import MeansTestRadioInput
from flask_babel import gettext as _
from app.means_test import YES, NO


class BaseMeansTestForm(FlaskForm):
    title = ""

    submit = SubmitField(_("Continue"), widget=GovSubmitInput())

    def payload(self) -> dict:
        return {}

    @classmethod
    def should_show(cls) -> bool:
        return True


class AboutYouForm(BaseMeansTestForm):
    title = "About you"

    template = "means_test/about-you.html"

    has_partner = RadioField(
        "Do you have a partner?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        description="Your husband, wife, civil partner (unless you have permanently separated) or someone you live with as if you're married",
        validators=[InputRequired(message=_("Tell us whether you have a partner"))],
    )

    are_you_in_a_dispute = RadioField(
        "Are you in a dispute with your partner?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        validators=[
            ValidateIf("has_partner", YES),
            InputRequired(
                message=_("Tell us whether you’re in dispute with your partner")
            ),
        ],
    )

    on_benefits = RadioField(
        "Do you receive any benefits (including Child Benefit)?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        description="Being on some benefits can help you qualify for legal aid",
        validators=[InputRequired(message=_("Tell us whether you receive benefits"))],
    )

    have_children = RadioField(
        "Do you have any children aged 15 or under?",
        choices=[(YES, "Yes"), (NO, "No")],
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
            ValidateIf("have_children", YES),
            InputRequired(
                message=_("Tell us how many children you have aged 15 or under")
            ),
            NumberRange(min=1, max=50, message=_("Enter a number between 1 and 50")),
        ],
    )

    have_dependents = RadioField(
        "Do you have any dependants aged 16 or over?",
        choices=[(YES, "Yes"), (NO, "No")],
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
            ValidateIf("have_dependents", YES),
            InputRequired(_("Tell us how many dependants you have aged 16 or over")),
            NumberRange(min=1, max=50, message=_("Enter a number between 1 and 50")),
        ],
    )

    own_property = RadioField(
        "Do you own any property?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        description="For example, a house, static caravan or flat",
        validators=[InputRequired(message=_("Tell us if you own any properties"))],
    )

    is_employed = RadioField(
        "Are you employed?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        description="This means working as an employee - you may be both employed and self-employed",
        validators=[InputRequired(message=_("Tell us if you are employed"))],
    )

    partner_is_employed = RadioField(
        _("Is your partner employed?"),
        description=_(
            "This means working as an employee - your partner may be both employed and self-employed"
        ),
        choices=[(YES, "Yes"), (NO, "No")],
        validators=[
            ValidateIf("are_you_in_a_dispute", NO),
            InputRequired(message=_("Tell us whether your partner is employed")),
        ],
        widget=MeansTestRadioInput(),
    )

    is_self_employed = RadioField(
        "Are you self-employed?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        description="This means working for yourself - you may be both employed and self-employed",
        validators=[InputRequired(message=_("Tell us if you are self-employed"))],
    )

    partner_is_self_employed = RadioField(
        _("Is your partner self-employed?"),
        description=_(
            "This means working for yourself - your partner may be both employed and self-employed"
        ),
        choices=[(YES, "Yes"), (NO, "No")],
        validators=[
            ValidateIf("are_you_in_a_dispute", NO),
            InputRequired(message=_("Tell us whether your partner is self-employed")),
        ],
        widget=MeansTestRadioInput(),
    )

    aged_60_or_over = RadioField(
        "Are you or your partner (if you have one) aged 60 or over?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        validators=[
            InputRequired(
                message=_("Tell us if you or your partner are aged 60 or over")
            )
        ],
    )

    have_savings = RadioField(
        "Do you have any savings or investments?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        validators=[
            InputRequired(message=_("Tell us whether you have savings or investments"))
        ],
    )

    have_valuables = RadioField(
        "Do you have any valuable items worth over £500 each?",
        choices=[(YES, "Yes"), (NO, "No")],
        widget=MeansTestRadioInput(),
        validators=[
            InputRequired(
                message=_("Tell us if you have any valuable items worth over £500 each")
            )
        ],
    )
