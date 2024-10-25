import pytest
from werkzeug.wrappers.response import Response


class MockQuestionForm:
    def __init__(self, title, valid_choices, routing_logic):
        self.title = title
        self._valid_choices = valid_choices
        self.routing_logic = routing_logic

    def valid_choices(self):
        return self._valid_choices


class MockResponse(Response):
    def __init__(self, status=302, location=None):
        super().__init__(status=status)
        if location:
            self.location = location


def mock_redirect(location):
    return MockResponse(location=location, status=302)


def mock_url_for(endpoint):
    return f"/mocked/{endpoint}"


def mock_abort(status_code):
    return MockResponse(status=status_code)


class TestCategoryTraversal:
    @pytest.fixture
    def mock_flask_redirects(self, monkeypatch):
        monkeypatch.setattr("app.categories.traversal.redirect", mock_redirect)
        monkeypatch.setattr("app.categories.traversal.url_for", mock_url_for)
        monkeypatch.setattr("app.categories.traversal.abort", mock_abort)

    @pytest.fixture
    def mock_form(self):
        """Creates an example form hierarchy for testing"""
        return MockQuestionForm(
            title="Question 1",
            valid_choices=["answer_a", "answer_b"],
            routing_logic={
                "answer_a": MockQuestionForm(
                    title="Question 2",
                    valid_choices=["answer_c", "answer_d"],
                    routing_logic={
                        "answer_c": "internal.endpoint.b",
                        "answer_d": MockResponse(
                            location="https://external-url-two.com"
                        ),
                    },
                ),
                "answer_b": "internal.endpoint.c",
            },
        )

    @pytest.fixture
    def category_traversal(self, mock_form, mock_flask_redirects):
        """Creates a CategoryTraversal instance with mocked routing logic"""
        from app.categories.traversal import CategoryTraversal

        CategoryTraversal.routing_logic = {
            "category_a": mock_form,
            "category_b": "internal.endpoint",
            "category_c": MockResponse(location="https://external-url.com"),
        }

        return CategoryTraversal()

    def test_invalid_category_returns_404(self, category_traversal):
        result = category_traversal.get_onward_question_from_path("invalid-category")
        assert isinstance(result, MockResponse)
        assert result.status_code == 404

    def test_internal_endpoint_category(self, category_traversal):
        result = category_traversal.get_onward_question_from_path("category_b")
        assert isinstance(result, MockResponse)
        assert result.location == "/mocked/internal.endpoint"

    def test_external_redirect_category(self, category_traversal):
        result = category_traversal.get_onward_question_from_path("category_c")
        assert isinstance(result, MockResponse)
        assert result.location == "https://external-url.com"

    def test_valid_path(self, category_traversal, mock_form):
        """You should either get a QuestionForm, an internal endpoint string or an HTTP Response"""
        # Test first level - Question Form
        result = category_traversal.get_onward_question_from_path("category_a")
        assert isinstance(result, MockQuestionForm)
        assert result.title == "Question 1"

        # Test second level - Question Form
        result = category_traversal.get_onward_question_from_path("category_a/answer_a")
        assert isinstance(result, MockQuestionForm)
        assert result.title == "Question 2"

        # Test second level
        result = category_traversal.get_onward_question_from_path("category_a/answer_a")
        assert isinstance(result, MockQuestionForm)
        assert result.title == "Question 2"

        # Test third level
        result = category_traversal.get_onward_question_from_path(
            "category_a/answer_a/answer_c"
        )
        assert isinstance(result, MockResponse)
        assert result.location == "/mocked/internal.endpoint.b"

        # Test third level - External Redirect
        result = category_traversal.get_onward_question_from_path(
            "category_a/answer_a/answer_d"
        )
        assert isinstance(result, MockResponse)
        assert result.location == "https://external-url-two.com"

    def test_invalid_path(self, category_traversal):
        """Asserts that you are taken back to the last valid answer you entered"""
        # Test invalid second level
        result = category_traversal.get_onward_question_from_path("category_a/invalid")
        assert isinstance(result, MockQuestionForm)
        assert result.title == "Question 1"

        # Test invalid third level
        result = category_traversal.get_onward_question_from_path(
            "category_a/answer_a/invalid"
        )
        assert isinstance(result, MockQuestionForm)
        assert result.title == "Question 2"
