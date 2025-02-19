from flask import session
from app.categories.family.urls import FamilyLandingPage


def test_category_page_dispatch(app):
    with app.app_context():
        page = FamilyLandingPage(FamilyLandingPage.template)
        page.dispatch_request()
        assert session.category == FamilyLandingPage.category
