import pytest
from unittest.mock import patch, Mock
from wtforms import Form
from flask import url_for
from app.means_test.views import MeansTest


class TestGetFormProgress:
    @pytest.fixture
    def mock_session(self):
        # Create a mock session with empty eligibility forms
        with patch("flask.session") as mock_session:
            eligibility = Mock()
            eligibility.forms = {}
            mock_session.get_eligibility.return_value = eligibility
            yield mock_session

    @pytest.fixture
    def forms_dict(self):
        # Base form class with required methods for testing
        class BaseTestForm(Form):
            @classmethod
            def should_show(cls):
                return True

            @property
            def page_title(self):
                return self._page_title

        # Create a form class for each form in the means test
        forms = {}
        for name in [
            "about-you",
            "benefits",
            "additional-benefits",
            "property",
            "savings",
            "income",
        ]:
            form_class = type(
                f"{name}Form",
                (BaseTestForm,),
                {"_page_title": name.replace("-", " ").title()},
            )
            forms[name] = form_class

        return forms

    @pytest.fixture
    def view(self, forms_dict, app, mock_session):
        # Set up test view with mock forms and test request context
        with app.test_request_context(), patch.object(MeansTest, "forms", forms_dict):
            yield MeansTest(forms_dict["about-you"], "about-you"), forms_dict

    @pytest.mark.parametrize(
        "current_form,completed_forms,expected_percentage",
        [
            # Percentage = (completed forms + current form) / (total forms + review & contact) * 100
            ("about-you", set(), 12.5),  # 1/8 * 100
            ("benefits", {"about-you"}, 25),  # 2/8 * 100
            (
                "savings",
                {"about-you", "benefits", "additional-benefits", "property", "income"},
                75,
            ),  # 6/8 * 100
        ],
    )
    def test_completion_percentage(
        self, view, current_form, completed_forms, expected_percentage
    ):
        test_view, forms = view
        test_view.form_class = forms[current_form]
        test_view.current_name = current_form

        # Patch is_form_completed to use our test's completed_forms set instead of the session
        with patch.object(
            MeansTest, "is_form_completed", side_effect=lambda x: x in completed_forms
        ):
            result = test_view.get_form_progress(forms[current_form]())
            assert result["completion_percentage"] == expected_percentage

    @pytest.mark.parametrize(
        "visible_forms,expected_steps",
        [
            # Test different combinations of visible forms
            (
                {
                    "about-you",
                    "benefits",
                    "additional-benefits",
                    "property",
                    "savings",
                    "income",
                },
                6,
            ),
            ({"about-you", "property", "savings", "income", "additional-benefits"}, 5),
            ({"about-you", "property", "savings", "income"}, 4),
            ({"about-you"}, 1),
        ],
    )
    def test_visible_steps(self, view, visible_forms, expected_steps):
        test_view, forms = view

        # Create a closure to properly capture form name for should_show method
        def create_should_show(form_name):
            def should_show(cls):
                return form_name in visible_forms

            return should_show

        # Configure which forms should be visible
        for name, form_class in forms.items():
            form_class.should_show = classmethod(create_should_show(name))

        with patch.object(MeansTest, "is_form_completed", return_value=False):
            result = test_view.get_form_progress(forms["about-you"]())
            assert len(result["steps"]) == expected_steps

    @pytest.mark.parametrize(
        "form_name", ["about-you", "benefits", "property", "income"]
    )
    def test_current_step_identification(self, view, form_name):
        test_view, forms = view
        test_view.form_class = forms[form_name]
        test_view.current_name = form_name

        with patch.object(MeansTest, "is_form_completed", return_value=False):
            result = test_view.get_form_progress(forms[form_name]())
            assert result["current_step"] == form_name

    def test_step_urls(self, view):
        test_view, forms = view

        with patch.object(MeansTest, "is_form_completed", return_value=False):
            result = test_view.get_form_progress(forms["about-you"]())
            for step in result["steps"]:
                assert step["url"] == url_for(f"means_test.{step['key']}")
