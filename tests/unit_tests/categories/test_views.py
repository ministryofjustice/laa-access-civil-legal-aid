from unittest.mock import Mock, patch
from flask import session
from app.categories.constants import FAMILY
from app.categories.family.urls import FamilyLandingPage
from app.categories.results.views import (
    OutOfScopePage,
    CannotFindYourProblemPage,
    NextStepsPage,
)


def test_category_page_dispatch(app):
    with app.app_context():
        page = FamilyLandingPage(FamilyLandingPage.template)
        page.dispatch_request()
        assert session.category == FamilyLandingPage.category


class TestOutOfScopePage:
    def test_init(self):
        page = OutOfScopePage("test.html", category=FAMILY)
        assert page.template == "test.html"
        assert page.category == FAMILY

    def test_dispatch_request(self, app):
        with app.test_request_context("/"):
            page = OutOfScopePage("test.html", category=FAMILY)

            # Mock get_context method
            expected_context = {"test_key": "test_value"}
            page.get_context = Mock(return_value=expected_context)


class TestCannotFindYourProblemPage:
    def test_init_default_next_steps(self):
        page = CannotFindYourProblemPage()
        assert page.template == "categories/cannot-find-problem.html"
        assert page.next_steps_page == "categories.results.next_steps"
        assert page.get_help_organisations is False

    def test_init_custom_next_steps(self):
        custom_next_steps = "custom.next.steps"
        page = CannotFindYourProblemPage(next_steps_page=custom_next_steps)
        assert page.next_steps_page == custom_next_steps

    def test_get_context(self):
        page = CannotFindYourProblemPage()

        parent_context = {"parent_key": "parent_value"}
        with patch.object(OutOfScopePage, "get_context", return_value=parent_context):
            context = page.get_context(FAMILY)

            assert context["parent_key"] == "parent_value"
            assert context["next_steps_page"] == page.next_steps_page


class TestNextStepsPage:
    def test_init(self):
        page = NextStepsPage()
        assert page.template == "categories/next-steps.html"

    def test_init_with_category(self):
        page = NextStepsPage(category=FAMILY)
        assert page.template == "categories/next-steps.html"
        assert page.category == FAMILY
