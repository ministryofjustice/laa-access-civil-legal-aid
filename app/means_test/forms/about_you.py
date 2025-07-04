from govuk_frontend_wtf.wtforms_widgets import GovTextInput
from wtforms.validators import InputRequired, NumberRange
from app.means_test.validators import ValidateIf
from app.main.widgets import MeansTestRadioInput
from flask_babel import lazy_gettext as _
from app.means_test.forms import BaseMeansTestForm
from app.means_test.fields import IntegerField, YesNoField


class AboutYouForm(BaseMeansTestForm):
    title = _("About you")

    template = "means_test/about-you.html"

    has_partner = YesNoField(
        _("Do you have a partner?"),
        widget=MeansTestRadioInput(),
        description=_(
            "Your husband, wife, civil partner (unless you have permanently separated) or someone you live with as if you're married"
        ),
        validators=[InputRequired(message=_("Tell us whether you have a partner"))],
    )

    in_dispute = YesNoField(
        _("Are you in a dispute with your partner?"),
        description=_(
            "This means your partner is the opponent in the dispute you need help with, for example a dispute over money or property"
        ),
        widget=MeansTestRadioInput(),
        validators=[
            ValidateIf("has_partner", True),
            InputRequired(message=_("Tell us whether you're in dispute with your partner")),
        ],
    )

    on_benefits = YesNoField(
        _("Do you receive any benefits (including Child Benefit)?"),
        widget=MeansTestRadioInput(),
        description=_("Being on some benefits can help you qualify for legal aid"),
        validators=[InputRequired(message=_("Tell us whether you receive benefits"))],
    )

    has_children = YesNoField(
        _("Do you have any children aged 15 or under?"),
        widget=MeansTestRadioInput(),
        description=_("Don't include any children who don't live with you"),
        validators=[InputRequired(message=_("Tell us whether you have any children aged 15 or under"))],
    )

    num_children = IntegerField(
        _("How many?"),
        widget=GovTextInput(),
        validators=[
            ValidateIf("has_children", True),
            InputRequired(message=_("Tell us how many children you have aged 15 or under")),
            NumberRange(min=1, max=50, message=_("Enter a number between 1 and 50")),
        ],
    )

    has_dependants = YesNoField(
        _("Do you have any dependants aged 16 or over?"),
        widget=MeansTestRadioInput(),
        description=_(
            "People who you live with and support financially. This could be a young person for whom you get Child Benefit"
        ),
        validators=[InputRequired(message=_("Tell us whether you have any dependants aged 16 or over"))],
    )

    num_dependants = IntegerField(
        _("How many?"),
        widget=GovTextInput(),
        validators=[
            ValidateIf("has_dependants", True),
            InputRequired(_("Tell us how many dependants you have aged 16 or over")),
            NumberRange(min=1, max=50, message=_("Enter a number between 1 and 50")),
        ],
    )

    own_property = YesNoField(
        _("Do you own any property?"),
        widget=MeansTestRadioInput(),
        description=_("For example, a house, static caravan or flat"),
        validators=[InputRequired(message=_("Tell us if you own any properties"))],
    )

    is_employed = YesNoField(
        _("Are you employed?"),
        widget=MeansTestRadioInput(),
        description=_("This means working as an employee - you may be both employed and self-employed"),
        validators=[InputRequired(message=_("Tell us if you are employed"))],
    )

    partner_is_employed = YesNoField(
        _("Is your partner employed?"),
        description=_("This means working as an employee - your partner may be both employed and self-employed"),
        validators=[
            ValidateIf("in_dispute", False),
            InputRequired(message=_("Tell us whether your partner is employed")),
        ],
        widget=MeansTestRadioInput(),
    )

    is_self_employed = YesNoField(
        _("Are you self-employed?"),
        widget=MeansTestRadioInput(),
        description=_("This means working for yourself - you may be both employed and self-employed"),
        validators=[InputRequired(message=_("Tell us if you are self-employed"))],
    )

    partner_is_self_employed = YesNoField(
        _("Is your partner self-employed?"),
        description=_("This means working for yourself - your partner may be both employed and self-employed"),
        validators=[
            ValidateIf("in_dispute", False),
            InputRequired(message=_("Tell us whether your partner is self-employed")),
        ],
        widget=MeansTestRadioInput(),
    )

    aged_60_or_over = YesNoField(
        _("Are you or your partner (if you have one) aged 60 or over?"),
        widget=MeansTestRadioInput(),
        validators=[InputRequired(message=_("Tell us if you or your partner are aged 60 or over"))],
    )

    has_savings = YesNoField(
        _("Do you have any savings or investments?"),
        widget=MeansTestRadioInput(),
        validators=[InputRequired(message=_("Tell us whether you have savings or investments"))],
    )

    has_valuables = YesNoField(
        _("Do you have any valuable items worth over £500 each?"),
        widget=MeansTestRadioInput(),
        validators=[InputRequired(message=_("Tell us if you have any valuable items worth over £500 each"))],
    )
