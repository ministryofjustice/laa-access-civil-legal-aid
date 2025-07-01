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
            "about-you": {"name": "Test User", "email": "test@example.com"},
            "benefits": {"receives_benefits": True},
            "savings": {"amount": 5000},
            "income": {"salary": 25000},
            "property": {"property_value": 200000},
        }
        return mock

    @pytest.fixture
    def mock_form(self):
        """Create a mock form with validate_on_submit returning False by default."""
        mock = Mock()
        mock.validate_on_submit.return_value = False
        mock.data = {}
        return mock

    def test_get_request_displays_form(self, app, client, mock_eligibility):
        """Test that a GET request displays the form."""
        with (
            patch(
                "app.means_test.views.session.get_eligibility",
                return_value=mock_eligibility,
            ),
            patch("app.means_test.views.render_template") as mock_render,
        ):
            response = client.get("/about-you")

            # Assert the response status
            assert response.status_code == 200
            # Verify render_template was called
            mock_render.assert_called_once()

    def test_form_submission_normal_flow(self, app, client, mock_eligibility, mock_url_for):
        """Test successful form submission with normal flow to next page."""
        # Create a mock form that validates successfully
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

            # Verify the form data was added to eligibility
            mock_eligibility.add.assert_called_once_with("benefits", {"benefits": "pension_credit"})

            mock_check_eligibility.assert_called()

            # Verify URL for next page was called
            mock_url_for.assert_called()

            # Verify redirect was called
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
