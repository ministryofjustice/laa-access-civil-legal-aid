from unittest.mock import patch, Mock
from app.means_test.payload import CFEMeansTestPayload
from app.means_test.money_interval import MoneyInterval
from app.categories.constants import FAMILY


class TestCFEMeansTestPayload:
    def test_init_creates_empty_payload(self, app):
        with app.app_context():
            with patch("app.means_test.payload.session"):
                payload = CFEMeansTestPayload()
                assert isinstance(payload, dict)
                assert len(payload) == 0

    def test_update_from_session_calls_all_processing_methods(self, app):
        with app.app_context():
            with patch("app.means_test.payload.session") as mock_session:
                mock_eligibility = Mock()
                mock_eligibility.forms = {"about-you": {"has_partner": True}}
                mock_session.get_eligibility = Mock(return_value=mock_eligibility)
                mock_session.category = FAMILY

                payload = CFEMeansTestPayload()

                with (
                    patch.object(payload, "update_from_form") as mock_update_form,
                    patch.object(payload, "_process_facts") as mock_process_facts,
                    patch.object(payload, "_handle_property_data") as mock_handle_property,
                    patch.object(payload, "_process_savings") as mock_process_savings,
                    patch.object(payload, "_process_benefits") as mock_process_benefits,
                    patch.object(payload, "_cleanup_payload") as mock_cleanup,
                    patch.object(payload, "_set_category") as mock_set_category,
                    patch.object(payload, "_convert_money_intervals") as mock_convert_money,
                ):
                    payload.update_from_session()

                    mock_update_form.assert_called_once_with("about-you", {"has_partner": True})
                    mock_process_facts.assert_called_once()
                    mock_handle_property.assert_called_once()
                    mock_process_savings.assert_called_once()
                    mock_process_benefits.assert_called_once()
                    mock_cleanup.assert_called_once()
                    mock_set_category.assert_called_once()
                    mock_convert_money.assert_called_once()

    def test_process_facts_moves_facts_to_facts_section(self, app):
        with app.app_context():
            payload = CFEMeansTestPayload()
            payload.update(
                {
                    "dependants_young": 2,
                    "dependants_old": 1,
                    "is_you_or_your_partner_over_60": True,
                    "has_partner": False,
                    "on_passported_benefits": True,
                    "on_nass_benefits": False,
                    "other_field": "should_remain",
                }
            )

            payload._process_facts()

            expected_facts = {
                "dependants_young": 2,
                "dependants_old": 1,
                "is_you_or_your_partner_over_60": True,
                "has_partner": False,
                "on_passported_benefits": True,
                "on_nass_benefits": False,
            }

            assert payload["facts"] == expected_facts
            assert "other_field" in payload
            for fact in expected_facts.keys():
                assert fact not in payload

    def test_process_facts_handles_missing_facts(self, app):
        with app.app_context():
            payload = CFEMeansTestPayload()
            payload.update({"some_other_field": "value"})

            payload._process_facts()

            assert payload["facts"] == {}
            assert "some_other_field" in payload

    def test_handle_property_data_with_property_set(self, app):
        with app.app_context():
            payload = CFEMeansTestPayload()
            property_data = [{"value": 200000, "mortgage_left": 100000}]
            payload["property_set"] = property_data

            payload._handle_property_data()

            assert payload["property_data"] == property_data
            assert "property_set" not in payload

    def test_handle_property_data_no_property_ownership(self, app):
        with app.app_context():
            with patch("app.means_test.payload.session") as mock_session:
                mock_eligibility = Mock()
                mock_eligibility.owns_property = False
                mock_session.get_eligibility = Mock(return_value=mock_eligibility)

                payload = CFEMeansTestPayload()
                payload["you"] = {
                    "deductions": {
                        "mortgage": MoneyInterval({"per_interval_value": 500, "interval_period": "per_month"})
                    }
                }

                payload._handle_property_data()

                assert payload["property_data"] == []
                assert payload["you"]["deductions"]["mortgage"] == 0

    def test_handle_property_data_owns_property_but_no_property_set(self, app):
        with app.app_context():
            with patch("app.means_test.payload.session") as mock_session:
                mock_eligibility = Mock()
                mock_eligibility.owns_property = True
                mock_session.get_eligibility = Mock(return_value=mock_eligibility)

                payload = CFEMeansTestPayload()

                payload._handle_property_data()

                expected_property = [
                    {"disputed": None, "main": None, "share": None, "value": None, "mortgage_left": None}
                ]
                assert payload["property_data"] == expected_property

    def test_process_savings_no_savings(self, app):
        with app.app_context():
            with patch("app.means_test.payload.session") as mock_session:
                mock_eligibility = Mock()
                mock_eligibility.has_savings = False
                mock_eligibility.has_valuables = False
                mock_session.get_eligibility = Mock(return_value=mock_eligibility)

                payload = CFEMeansTestPayload()
                payload["you"] = {}

                payload._process_savings()

                expected_savings = {"bank_balance": 0, "investment_balance": 0, "asset_balance": 0, "credit_balance": 0}
                assert payload["you"]["savings"] == expected_savings

    def test_process_savings_with_existing_savings(self, app):
        with app.app_context():
            with patch("app.means_test.payload.session") as mock_session:
                mock_eligibility = Mock()
                mock_eligibility.has_savings = True
                mock_session.get_eligibility = Mock(return_value=mock_eligibility)

                payload = CFEMeansTestPayload()
                payload["you"] = {"savings": {"bank_balance": 5000}}

                payload._process_savings()

                assert payload["you"]["savings"]["credit_balance"] == 0
                assert payload["you"]["savings"]["bank_balance"] == 5000

    def test_process_benefits_adds_benefits_if_missing(self, app):
        with app.app_context():
            payload = CFEMeansTestPayload()
            payload["you"] = {"income": {"earnings": 1000}}

            payload._process_benefits()

            assert payload["you"]["income"]["benefits"] == 0

    def test_process_benefits_does_nothing_if_benefits_exist(self, app):
        with app.app_context():
            payload = CFEMeansTestPayload()
            payload["you"] = {"income": {"benefits": 500}}

            payload._process_benefits()

            assert payload["you"]["income"]["benefits"] == 500

    def test_process_benefits_does_nothing_if_no_income(self, app):
        with app.app_context():
            payload = CFEMeansTestPayload()
            payload["you"] = {}

            payload._process_benefits()

            assert "income" not in payload["you"]

    def test_cleanup_payload_removes_unwanted_fields(self, app):
        with app.app_context():
            payload = CFEMeansTestPayload()
            payload.update(
                {"notes": "Some notes", "specific_benefits": {"universal_credit": True}, "important_field": "keep_this"}
            )

            payload._cleanup_payload()

            assert "notes" not in payload
            assert "specific_benefits" not in payload
            assert payload["important_field"] == "keep_this"

    def test_set_category(self, app):
        with app.app_context():
            with patch("app.means_test.payload.session") as mock_session:
                mock_session.category = FAMILY

                payload = CFEMeansTestPayload()
                payload._set_category()

                assert payload["category"] == "family"

    def test_convert_money_intervals_converts_you_section(self, app):
        with app.app_context():
            payload = CFEMeansTestPayload()
            payload["you"] = {
                "income": {
                    "earnings": MoneyInterval(
                        {"per_interval_value": 480000, "interval_period": "per_week"}
                    ),  # £4800/week = £20,800/month
                    "benefits": 500,
                },
                "deductions": {
                    "rent": MoneyInterval(
                        {"per_interval_value": 200000, "interval_period": "per_4week"}
                    ),  # £2000/4week = £2166.67/month
                    "other": 100,
                },
            }

            payload._convert_money_intervals()

            assert payload["you"]["income"]["earnings"] == 2079999  # £480/week converted to monthly
            assert payload["you"]["income"]["benefits"] == 500
            assert payload["you"]["deductions"]["rent"] == 216666  # £2000/4week converted to monthly
            assert payload["you"]["deductions"]["other"] == 100

    def test_convert_money_intervals_converts_partner_section(self, app):
        with app.app_context():
            payload = CFEMeansTestPayload()
            payload["partner"] = {
                "income": {
                    "earnings": MoneyInterval(
                        {"per_interval_value": 1800000, "interval_period": "per_year"}
                    )  # £18,000/year = £1,500/month
                }
            }

            payload._convert_money_intervals()

            assert payload["partner"]["income"]["earnings"] == 150000  # £1,500/month in pence

    def test_convert_money_intervals_handles_missing_sections(self, app):
        with app.app_context():
            payload = CFEMeansTestPayload()
            payload["you"] = {"other_data": "value"}

            payload._convert_money_intervals()

            assert payload["you"]["other_data"] == "value"

    def test_convert_money_intervals_handles_missing_person(self, app):
        with app.app_context():
            payload = CFEMeansTestPayload()
            payload["some_other_field"] = "value"

            payload._convert_money_intervals()

            assert payload["some_other_field"] == "value"

    def test_full_integration_with_mock_session(self, app):
        with app.app_context():
            with patch("app.means_test.payload.session") as mock_session:
                mock_eligibility = Mock()
                mock_eligibility.forms = {"about-you": {"has_partner": True, "dependants_young": 2}}
                mock_eligibility.owns_property = False
                mock_eligibility.has_savings = False
                mock_session.get_eligibility = Mock(return_value=mock_eligibility)
                mock_session.category = FAMILY

                payload = CFEMeansTestPayload()

                with patch.object(payload, "update_from_form") as mock_update_form:
                    mock_update_form.side_effect = lambda form, data: payload.update(
                        {
                            "dependants_young": data.get("dependants_young", 0),
                            "has_partner": data.get("has_partner", False),
                            "you": {
                                "income": {},
                                "deductions": {
                                    "mortgage": MoneyInterval({"per_interval_value": 0, "interval_period": "per_month"})
                                },
                            },
                        }
                    )

                    payload.update_from_session()

                assert "facts" in payload
                assert payload["facts"]["dependants_young"] == 2
                assert payload["facts"]["has_partner"]
                assert payload["property_data"] == []
                assert payload["you"]["deductions"]["mortgage"] == 0
                assert payload["category"] == "family"
                assert "notes" not in payload
                assert "specific_benefits" not in payload
