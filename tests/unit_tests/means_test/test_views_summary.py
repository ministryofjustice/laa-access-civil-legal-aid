from unittest import mock
from flask_babel import lazy_gettext as _
from app.means_test.views import CheckYourAnswers, ReviewForm
from app.means_test import YES, NO
from app.session import Eligibility
from app.categories.models import CategoryAnswer
from app.categories.constants import DISCRIMINATION, HOUSING


def mock_render_template(template_name, **kwargs):
    return kwargs


def mock_session_get_eligibility():
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
                "benefits": {"benefits": ["employment_support", "universal_credit"]},
            }
        }
    )


@mock.patch("app.means_test.views.render_template", mock_render_template)
@mock.patch(
    "app.means_test.views.session.get_eligibility", mock_session_get_eligibility
)
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
        summary = CheckYourAnswers().get()
        assert summary["means_test_summary"] == expected_summary

        assert isinstance(summary["form"], ReviewForm)


def test_get_category_answers_summary_no_description(app):
    expected_summary = [
        {
            "key": {"text": _("The problem you need help with")},
            "value": {"text": _("Discrimination")},
            "actions": {"items": [{"text": _("Change"), "href": "/find-your-problem"}]},
        },
        {
            "key": {"text": "Where did the discrimination happen?"},
            "value": {
                "text": "Work - including colleagues, employer or employment agency"
            },
            "actions": {
                "items": [{"text": _("Change"), "href": "/discrimination/where"}]
            },
        },
        {
            "key": {"text": "Why were you discriminated against?"},
            "value": {"text": "Disability, health condition, mental health condition"},
            "actions": {
                "items": [{"text": _("Change"), "href": "/discrimination/why"}]
            },
        },
        {
            "key": {"text": "Are you under 18?"},
            "value": {"text": "No"},
            "actions": {
                "items": [{"text": _("Change"), "href": "/discrimination/age"}]
            },
        },
    ]

    category_mocker = mock.patch(
        "app.session.Session.category",
        new_callable=mock.PropertyMock,
        return_value=DISCRIMINATION,
    )
    category_mocker.start()

    mock_category_answers = [
        CategoryAnswer(
            question="Where did the discrimination happen?",
            category=DISCRIMINATION,
            answer_label="Work - including colleagues, employer or employment agency",
            answer_value="work",
            next_page="categories.discrimination.why",
            question_page="categories.discrimination.where",
        ),
        CategoryAnswer(
            question="Why were you discriminated against?",
            category=DISCRIMINATION,
            answer_label="Disability, health condition, mental health condition",
            answer_value="disability",
            next_page="categories.discrimination.age",
            question_page="categories.discrimination.why",
        ),
        CategoryAnswer(
            question="Are you under 18?",
            category=DISCRIMINATION,
            answer_label="No",
            answer_value="no",
            next_page="categories.index",
            question_page="categories.discrimination.age",
        ),
    ]

    with app.app_context():
        with mock.patch(
            "app.session.Session.category_answers", new_callable=mock.PropertyMock
        ) as mocker:
            mocker.return_value = mock_category_answers
            summary = CheckYourAnswers().get_category_answers_summary()
        assert summary == expected_summary

    category_mocker.stop()


def test_get_category_answers_summary_with_description(app):
    expected_summary = [
        {
            "key": {"text": _("The problem you need help with")},
            "value": {
                "markdown": "**Homelessness**\nHelp if you’re homeless, or might be homeless in the next 2 months. This could be because of rent arrears, debt, the end of a relationship, or because you have nowhere to live."
            },
            "actions": {"items": [{"text": _("Change"), "href": "/housing/"}]},
        },
        {
            "key": {"text": "Are you under 18?"},
            "value": {"text": "No"},
            "actions": {
                "items": [{"text": _("Change"), "href": "/discrimination/age"}]
            },
        },
    ]

    mock_category_answers = [
        CategoryAnswer(
            question="Homelessness",
            category=HOUSING.sub.homelessness,
            answer_label="Homelessness",
            answer_value="homelessness",
            next_page="categories.discrimination.age",
            question_page="categories.housing.landing",
        ),
        CategoryAnswer(
            question="Are you under 18?",
            category=HOUSING.sub.homelessness,
            answer_label="No",
            answer_value="no",
            next_page="categories.index",
            question_page="categories.discrimination.age",
        ),
    ]

    category_mocker = mock.patch(
        "app.session.Session.category", new_callable=mock.PropertyMock
    )
    category_mocker.return_value = HOUSING
    category_mocker.start()

    with app.app_context():
        with mock.patch(
            "app.session.Session.category_answers", new_callable=mock.PropertyMock
        ) as mocker:
            mocker.return_value = mock_category_answers
            summary = CheckYourAnswers().get_category_answers_summary()
        assert summary == expected_summary

    category_mocker.stop()
