import pytest
from unittest.mock import patch, Mock
from app.means_test.forms.income import IncomeForm
from flask_babel import lazy_gettext as _


TEST_CASES = {
    "employed_with_employed_partner": (
        {
            "is_employed": True,
            "is_self_employed": False,
            "has_partner": True,
            "is_partner_employed": True,
            "is_partner_self_employed": False,
        },
        {
            "self": [
                "earnings",
                "income_tax",
                "working_tax_credit",
                "maintenance_received",
                "pension",
                "other_income",
            ],
            "partner": [
                "partner_earnings",
                "partner_income_tax",
                "partner_working_tax_credit",
                "partner_maintenance_received",
                "partner_pension",
                "partner_other_income",
            ],
        },
        {
            "title": _("You and your partner’s income and tax"),
        },
    ),
    "self_employed_no_partner": (
        {
            "is_employed": False,
            "is_self_employed": True,
            "has_partner": False,
            "is_partner_employed": False,
            "is_partner_self_employed": False,
        },
        {
            "self": [
                "earnings",
                "income_tax",
                "working_tax_credit",
                "maintenance_received",
                "pension",
                "other_income",
            ],
            "partner": [],
        },
        {
            "title": _("Your income and tax"),
        },
    ),
    "unemployed_employed_partner": (
        {
            "is_employed": False,
            "is_self_employed": False,
            "has_partner": True,
            "is_partner_employed": True,
            "is_partner_self_employed": False,
        },
        {
            "self": ["maintenance_received", "pension", "other_income"],
            "partner": [
                "partner_earnings",
                "partner_income_tax",
                "partner_working_tax_credit",
                "partner_maintenance_received",
                "partner_pension",
                "partner_other_income",
            ],
        },
        {
            "title": _("You and your partner’s money coming in"),
        },
    ),
    "unemployed_no_partner": (
        {
            "is_employed": False,
            "is_self_employed": False,
            "has_partner": False,
            "is_partner_employed": False,
            "is_partner_self_employed": False,
        },
        {"self": ["maintenance_received", "pension", "other_income"], "partner": []},
        {
            "title": _("Your money coming in"),
        },
    ),
}


@pytest.mark.parametrize(
    "eligibility_data,expected_fields, expected_title",
    TEST_CASES.values(),
    ids=TEST_CASES.keys(),
)
def test_shown_fields(client, eligibility_data, expected_fields, expected_title):
    mock_eligibility = Mock()
    mock_eligibility.is_employed = eligibility_data["is_employed"]
    mock_eligibility.is_self_employed = eligibility_data["is_self_employed"]
    mock_eligibility.has_partner = eligibility_data["has_partner"]
    mock_eligibility.is_partner_employed = eligibility_data["is_partner_employed"]
    mock_eligibility.is_partner_self_employed = eligibility_data[
        "is_partner_self_employed"
    ]

    with patch(
        "app.means_test.forms.income.session.get_eligibility",
        return_value=mock_eligibility,
    ):
        income_form = IncomeForm()
        actual_fields = income_form.shown_fields

        assert len(actual_fields["self"]) == len(expected_fields["self"])
        assert len(actual_fields["partner"]) == len(expected_fields["partner"])

        assert [field.name for field in actual_fields["self"]] == expected_fields[
            "self"
        ]
        assert [field.name for field in actual_fields["partner"]] == expected_fields[
            "partner"
        ]
        assert income_form.page_title == expected_title["title"]
