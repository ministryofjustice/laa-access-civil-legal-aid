import pytest
from unittest.mock import patch, Mock, PropertyMock
from app.means_test.constants import EligibilityState
from app.means_test.views import MeansTest, InScopeMixin, CheckYourAnswers


@pytest.fixture
def mock_url_for():
    with patch("app.means_test.views.url_for") as mock:

        def side_effect(*args, **kwargs):
            if kwargs and "endpoint" in kwargs:
                return f"/mocked/{kwargs['endpoint']}"
            return f"/mocked/{args[0]}"

        mock.side_effect = side_effect
        yield mock


@patch.object(InScopeMixin, "ensure_in_scope", return_value=None)
class TestDispatchRequest:
    @pytest.fixture
    def mock_eligibility(self):
        mock = Mock()
        mock.forms = {
            "about-you": {
                "aged_60_or_over": False,
                "has_children": False,
                "has_dependants": False,
                "has_partner": False,
                "has_savings": True,
                "has_valuables": False,
                "in_dispute": None,
                "is_employed": False,
                "is_self_employed": False,
                "num_children": None,
                "num_dependants": None,
                "on_benefits": False,
                "own_property": True,
                "partner_is_employed": None,
                "partner_is_self_employed": None,
            },
            "savings": {"investments": 60000, "savings": 70000, "valuables": None},
            "income": {
                "child_tax_credit": {
                    "interval_period": None,
                    "per_interval_value": None,
                },
                "earnings": {"interval_period": None, "per_interval_value": None},
                "income_tax": {"interval_period": None, "per_interval_value": None},
                "maintenance_received": {
                    "interval_period": "per_month",
                    "per_interval_value": 100000,
                },
                "national_insurance": {
                    "interval_period": None,
                    "per_interval_value": None,
                },
                "other_income": {
                    "interval_period": "per_month",
                    "per_interval_value": 3000,
                },
                "partner_earnings": {
                    "interval_period": None,
                    "per_interval_value": None,
                },
                "partner_income_tax": {
                    "interval_period": None,
                    "per_interval_value": None,
                },
                "partner_maintenance_received": {
                    "interval_period": None,
                    "per_interval_value": None,
                },
                "partner_national_insurance": {
                    "interval_period": None,
                    "per_interval_value": None,
                },
                "partner_other_income": {
                    "interval_period": None,
                    "per_interval_value": None,
                },
                "partner_pension": {
                    "interval_period": None,
                    "per_interval_value": None,
                },
                "partner_working_tax_credit": {
                    "interval_period": None,
                    "per_interval_value": None,
                },
                "pension": {
                    "interval_period": "per_month",
                    "per_interval_value": 2000,
                },
                "working_tax_credit": {
                    "interval_period": None,
                    "per_interval_value": None,
                },
            },
            "property": {
                "properties": [
                    {
                        "csrf_token": None,
                        "in_dispute": False,
                        "is_main_home": True,
                        "is_rented": False,
                        "mortgage_payments": 100000,
                        "mortgage_remaining": 200000,
                        "other_shareholders": False,
                        "property_value": 1000000,
                        "rent_amount": {
                            "interval_period": None,
                            "per_interval_value": None,
                            "per_interval_value_pounds": None,
                        },
                    }
                ]
            },
        }
        return mock

    @pytest.fixture
    def mock_form(self):
        mock = Mock()
        mock.validate_on_submit.return_value = False
        mock.data = {}
        return mock

    def test_get_request_displays_form(self, app, client, mock_eligibility):
        with (
            patch(
                "app.means_test.views.session.get_eligibility",
                return_value=mock_eligibility,
            ),
            patch("app.means_test.views.render_template") as mock_render,
        ):
            response = client.get("/about-you")

            assert response.status_code == 200
            mock_render.assert_called_once()

    def test_form_submission_normal_flow(self, app, client, mock_eligibility, mock_url_for):
        mock_form = Mock()
        mock_form.validate_on_submit.return_value = True
        mock_form.data = {"benefits": "pension_credit"}

        with (
            app.test_request_context("/benefits", method="POST"),
            patch(
                "app.means_test.views.session.get_eligibility",
                return_value=mock_eligibility,
            ),
            patch("app.means_test.views.check_eligibility") as mock_check_eligibility,
            patch("app.means_test.views.BenefitsForm", return_value=mock_form),
            patch("app.means_test.views.redirect") as mock_redirect,
            patch(
                "app.means_test.views.MeansTest.ensure_form_protection",
                return_value=None,
            ),
        ):
            view = MeansTest.as_view("benefits", Mock(return_value=mock_form), "benefits")
            view()

            mock_eligibility.add.assert_called_once_with("benefits", {"benefits": "pension_credit"})

            mock_check_eligibility.assert_called()

            mock_url_for.assert_called()

            mock_redirect.assert_called_once()

    def test_redirect_to_review_when_eligible(self, app, client, mock_eligibility, mock_url_for):
        """Test that form submission redirects to review page when eligibility is determined."""
        mock_form = Mock()
        mock_form.validate_on_submit.return_value = True
        mock_form.data = {"salary": 30000}

        with (
            app.test_request_context("/income", method="POST"),
            patch(
                "app.means_test.views.session.get_eligibility",
                return_value=mock_eligibility,
            ),
            patch("app.means_test.views.IncomeForm", return_value=mock_form),
            patch("app.means_test.views.check_eligibility") as mock_check_eligibility,
            patch("app.means_test.views.redirect") as mock_redirect,
            patch(
                "app.means_test.views.MeansTest.ensure_form_protection",
                return_value=None,
            ),
        ):
            from app.means_test.views import MeansTest

            view = MeansTest.as_view("income", Mock(return_value=mock_form), "income")
            view()

            mock_check_eligibility.assert_called()

            mock_url_for.assert_called_with("means_test.review")

            mock_redirect.assert_called_once()


@patch.object(InScopeMixin, "ensure_in_scope", return_value=None)
class TestCheckYourAnswersSubmission:
    @pytest.mark.parametrize("eligibility", [EligibilityState.YES, EligibilityState.UNKNOWN])
    def test_post_eligible(self, app, client, mock_url_for, eligibility):
        """Test post method when eligibility state is YES/ UNKNOWN."""
        with client.session_transaction() as session:
            session["ec_reference"] = "test-reference"
            session["eligibility_result"] = eligibility

        with (
            patch("app.means_test.views.redirect") as mock_redirect,
            patch.object(CheckYourAnswers, "ensure_all_forms_are_complete", return_value=None),
        ):
            client.post("/review")

            mock_url_for.assert_called_once_with("contact.eligible")
            mock_redirect.assert_called_once_with("/mocked/contact.eligible")

    def test_post_ineligible_with_hlpas(self, app, client, mock_url_for):
        """Test post method when ineligible but eligible for HLPAS."""
        with client.session_transaction() as sess:
            sess["ec_reference"] = "test-reference"
            sess["eligibility_result"] = EligibilityState.NO

        with (
            patch("app.means_test.views.redirect") as mock_redirect,
            patch("app.means_test.views.session") as mock_session,
            patch.object(CheckYourAnswers, "ensure_all_forms_are_complete", return_value=None),
        ):
            mock_subcategory = Mock()
            mock_subcategory.eligible_for_HLPAS = True

            type(mock_session).subcategory = PropertyMock(return_value=mock_subcategory)

            client.post("/review")

            mock_url_for.assert_called_once_with("means_test.result.hlpas")
            mock_redirect.assert_called_once_with("/mocked/means_test.result.hlpas")

    def test_post_ineligible_subcategory_no_hlpas(self, app, client, mock_url_for):
        """Test post method when ineligible with subcategory but not eligible for HLPAS."""
        with client.session_transaction() as sess:
            sess["ec_reference"] = "test-reference"
            sess["eligibility_result"] = EligibilityState.NO

        with (
            patch("app.means_test.views.redirect") as mock_redirect,
            patch("app.means_test.views.session") as mock_session,
            patch.object(CheckYourAnswers, "ensure_all_forms_are_complete", return_value=None),
        ):
            mock_subcategory = Mock()
            mock_subcategory.eligible_for_HLPAS = False
            type(mock_session).subcategory = PropertyMock(return_value=mock_subcategory)

            client.post("/review")

            mock_url_for.assert_called_once_with("means_test.result.ineligible")
            mock_redirect.assert_called_once_with("/mocked/means_test.result.ineligible")
