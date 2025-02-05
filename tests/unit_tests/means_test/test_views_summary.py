from unittest import mock
from flask_babel import lazy_gettext as _
from app.means_test.views import CheckYourAnswers, ReviewForm
from app.means_test import YES, NO
from app.session import Eligibility


class TestCheckYourAnswersView(CheckYourAnswers):
    def get_eligibility(self):
        return Eligibility(
            **{
                "forms": {
                    "about-you": {
                        "has_partner": NO,
                        "on_benefits": YES,
                        "have_children": NO,
                        "have_dependents": NO,
                        "own_property": NO,
                    },
                    "benefits": {
                        "benefits": ["employment_support", "universal_credit"]
                    },
                }
            }
        )


def mock_render_template(template_name, **kwargs):
    return kwargs


@mock.patch("app.means_test.views.render_template", mock_render_template)
def test_views_summary(app):
    expected_summary = {
        "About you": [
            {
                "key": {"text": "Do you have a partner?"},
                "value": {"text": "No"},
                "actions": {
                    "items": [{"href": "/about-you#has_partner", "text": _("Change")}]
                },
            },
            {
                "key": {
                    "text": "Do you receive any benefits (including Child Benefit)?"
                },
                "value": {"text": "Yes"},
                "actions": {
                    "items": [{"href": "/about-you#on_benefits", "text": _("Change")}]
                },
            },
            {
                "key": {"text": "Do you have any children aged 15 or under?"},
                "value": {"text": "No"},
                "actions": {
                    "items": [{"href": "/about-you#have_children", "text": _("Change")}]
                },
            },
            {
                "key": {"text": "Do you have any dependants aged 16 or over?"},
                "value": {"text": "No"},
                "actions": {
                    "items": [
                        {"href": "/about-you#have_dependents", "text": _("Change")}
                    ]
                },
            },
            {
                "key": {"text": "Do you own any property?"},
                "value": {"text": "No"},
                "actions": {
                    "items": [{"href": "/about-you#own_property", "text": _("Change")}]
                },
            },
        ],
        "Which benefits do you receive?": [
            {
                "key": {"text": "Which benefits do you receive?"},
                "value": {
                    "markdown": "Income-related Employment and Support Allowance\nUniversal Credit"
                },
                "actions": {
                    "items": [{"href": "/benefits#benefits", "text": _("Change")}]
                },
            }
        ],
    }

    with app.app_context():
        summary = TestCheckYourAnswersView().get()
        assert summary["means_test_summary"] == expected_summary
        assert isinstance(summary["form"], ReviewForm)
