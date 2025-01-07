from flask_wtf import FlaskForm
from wtforms.fields import RadioField

from app.means_test.widgets import MeansTestRadioInput


class AboutYouForm(FlaskForm):
    title = "About you"

    partner = RadioField(
        "Do you have a partner?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        description="Your husband, wife, civil partner (unless you have permanently separated) or someone you live with as if you're married",
    )

    are_you_in_a_dispute = RadioField(
        "Are you in a dispute with your partner?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
    )

    do_you_receive_benefits = RadioField(
        "Do you receive any benefits (including Child Benefit)?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        description="Being on some benefits can help you qualify for legal aid",
    )

    children_under_16 = RadioField(
        "Do you have any children aged 15 or under?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        description="Don't include any children who don't live with you",
    )

    dependants_over_16 = RadioField(
        "Do you have any dependants aged 16 or over?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        description="People who you live with and support financially. This could be a young person for whom you get Child Benefit",
    )

    own_property = RadioField(
        "Do you own any property?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        description="For example, a house, static caravan or flat",
    )

    employed = RadioField(
        "Are you employed?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        description="This means working as an employee - you may be both employed and self-employed",
    )

    self_employed = RadioField(
        "Are you self-employed?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
        description="This means working for yourself - you may be both employed and self-employed",
    )

    over_60 = RadioField(
        "Are you or your partner (if you have one) aged 60 or over?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
    )

    savings_or_investments = RadioField(
        "Do you have any savings or investments?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
    )

    valuable_items = RadioField(
        "Do you have any valuable items worth over £500 each?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=MeansTestRadioInput(),
    )
