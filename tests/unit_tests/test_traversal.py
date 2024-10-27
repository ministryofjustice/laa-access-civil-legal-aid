import pytest
from werkzeug.exceptions import NotFound
from wtforms.fields.choices import RadioField

from app.categories.forms import QuestionForm
from app.categories.redirect import CheckDestination, CheckRedirect
from app.categories.traversal import CategoryTraversal, InitialCategoryQuestion


@pytest.fixture
def mock_nested_form():
    class MockNestedForm(QuestionForm):
        title = "Nested Question"
        routing_logic = {"final_a": "final-endpoint-a", "final_b": "final-endpoint-b"}

        question = RadioField(
            title,
            choices=[
                ("final_a", "Final A"),
                ("final_b", "Final B"),
            ],
        )

    return MockNestedForm


@pytest.fixture
def mock_subcategory_form_a(mock_nested_form):
    class MockSubCategoryFormA(QuestionForm):
        title = "Sub Category A Question"
        routing_logic = {
            "to_form": mock_nested_form,  # Leads to another form
            "to_internal": "internal-endpoint",  # Internal redirect
            "to_check": CheckRedirect(destination=CheckDestination.MEANS_TEST),
        }

        question = RadioField(
            title,
            choices=[
                ("to_form", "To Next Form"),
                ("to_internal", "To Internal"),
                ("to_contact", CheckRedirect(destination=CheckDestination.CONTACT)),
            ],
        )

    return MockSubCategoryFormA


@pytest.fixture
def mock_subcategory_form_b(mock_nested_form):
    class MockSubCategoryFormB(QuestionForm):
        title = "Sub Category B Question"
        routing_logic = {
            "to_form": mock_nested_form,
            "to_internal": "internal-endpoint-b",
            "to_external": CheckRedirect(CheckDestination.MEANS_TEST),
        }

    return MockSubCategoryFormB


@pytest.fixture
def test_initial_form(mock_subcategory_form_a, mock_subcategory_form_b):
    class TestInitialForm(InitialCategoryQuestion):
        title = "Initial Question"
        routing_logic = {
            "category_a": mock_subcategory_form_a,
            "category_b": mock_subcategory_form_b,
            "category_c": CheckRedirect(CheckDestination.FALA),
        }

        category_labels = {
            "category_a": "Category A Label",
            "category_b": "Category B Label",
            "category_c": "Category C Label",
        }

    return TestInitialForm


def test_category_traversal(test_initial_form):
    traversal = CategoryTraversal(test_initial_form)

    assert "category_a/to_form/final_a" in traversal.route_cache
    assert "category_a/to_form/final_b" in traversal.route_cache

    result_a = traversal.navigate_path("category_a/to_form/final_a")
    assert result_a.internal_redirect == "final-endpoint-a"

    result_b = traversal.navigate_path("category_a/to_form/final_b")
    assert result_b.internal_redirect == "final-endpoint-b"


def test_category_traversal_invalid_path(test_initial_form):
    traversal = CategoryTraversal(test_initial_form)

    with pytest.raises(NotFound):
        traversal.navigate_path("invalid/path")

    with pytest.raises(NotFound):
        traversal.navigate_path("category_a/invalid")

    with pytest.raises(NotFound):
        traversal.navigate_path("category_a/to_form/invalid")


def test_category_traversal_empty_path(test_initial_form):
    traversal = CategoryTraversal(test_initial_form)

    result = traversal.navigate_path("")
    assert result.question_form == test_initial_form
    assert result.is_redirect is False


@pytest.mark.parametrize(
    "path,expected_type",
    [
        ("", "question_form"),
        ("category_a", "question_form"),
        ("category_a/to_form", "question_form"),
        ("category_a/to_internal", "internal_redirect"),
        ("category_a/to_check", "external_redirect"),
        ("category_a/to_form/final_a", "internal_redirect"),
        ("category_c", "external_redirect"),
    ],
)
def test_category_traversal_navigation_result_types(
    test_initial_form, path, expected_type
):
    traversal = CategoryTraversal(test_initial_form)
    result = traversal.navigate_path(path)

    if expected_type == "question_form":
        assert result.question_form is not None
        assert result.internal_redirect is None
        assert result.check_redirect is None
    elif expected_type == "internal_redirect":
        assert result.question_form is None
        assert result.internal_redirect is not None
        assert result.check_redirect is None
    else:  # external_redirect
        assert result.question_form is None
        assert result.internal_redirect is None
        assert result.check_redirect is not None


def test_initial_category_question_get_label(test_initial_form):
    assert test_initial_form.get_label("category_a") == "Category A Label"
    assert test_initial_form.get_label("category_b") == "Category B Label"
    assert test_initial_form.get_label("unknown") == "unknown"


def test_initial_category_question_valid_choices(test_initial_form):
    choices = test_initial_form.valid_choices()
    assert set(choices) == {"category_a", "category_b", "category_c"}


@pytest.mark.parametrize(
    "path,expected_map",
    [
        ("", {}),  # Empty path
        (
            "invalid/path",
            {
                "Initial Question": "invalid choice",
            },
        ),
        (
            "category_a/invalid_answer",
            {
                "Initial Question": "Category A Label",
                "Sub Category A Question": "invalid choice",
            },
        ),
        ("category_a", {"Initial Question": "Category A Label"}),
        (
            "category_a/to_form",
            {
                "Initial Question": "Category A Label",
                "Sub Category A Question": "To Next Form",
            },
        ),
        (
            "category_a/to_form/final_a",
            {
                "Initial Question": "Category A Label",
                "Sub Category A Question": "To Next Form",
                "Nested Question": "Final A",
            },
        ),
        (
            "category_a/to_internal",
            {
                "Initial Question": "Category A Label",
                "Sub Category A Question": "To Internal",
            },
        ),
    ],
)
def test_get_question_answer_map(test_initial_form, path, expected_map):
    traversal = CategoryTraversal(test_initial_form)
    result = traversal.get_question_answer_map(path)
    assert result == expected_map
