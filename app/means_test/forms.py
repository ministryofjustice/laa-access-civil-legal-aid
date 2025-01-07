from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovRadioInput
from wtforms.fields import RadioField


class AboutYouForm(FlaskForm):
    title = "About you"

    partner = RadioField(
        "Do you have a partner?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=GovRadioInput(),
        description="Your husband, wife, civil partner (unless you have permanently separated) or someone you live with as if you’re married",
    )

    are_you_in_a_dispute = RadioField(
        "Are you in a dispute with your partner?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=GovRadioInput(),
    )

    do_you_receive_benefits = RadioField(
        "Do you receive any benefits (including Child Benefit)?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=GovRadioInput(),
        description="Being on some benefits can help you qualify for legal aid",
    )
