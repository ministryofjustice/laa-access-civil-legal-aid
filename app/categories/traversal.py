from dataclasses import dataclass
from flask import url_for
from werkzeug.exceptions import NotFound

from app.categories.forms import QuestionForm
from app.categories.questions.discrimination import DiscriminationWhereForm
from app.categories.questions.domestic_abuse import DomesticAbuseTraversal
from app.categories.redirect import CheckRedirect, CheckDestination, CheckCategory


class InitialCategoryQuestion(QuestionForm):
    title = "What do you need help with?"

    routing_logic = {
        "discrimination": DiscriminationWhereForm,
        "domestic-abuse": DomesticAbuseTraversal,
        "clinical-negligence": CheckRedirect(
            CheckDestination.FALA, category=CheckCategory.CLINICAL_NEGLIGENCE
        ),
    }

    category_labels = {
        "discrimination": "Discrimination",
        "domestic-abuse": "Domestic abuse",
        "clinical-negligence": "Clinical negligence in babies",
    }

    @classmethod
    def get_choice_label(cls, choice: str) -> str:
        """Convert a category value to its human-readable label.
            If there is no alternative then will fallback and return the internal value.

        Args:
            choice: The internal choice value (e.g. "asylum")

        Returns:
            The display label (e.g., "Asylum and immigration")
        """
        return dict(cls.category_labels).get(choice, choice)

    @classmethod
    def valid_choices(cls) -> list[str]:
        return list(cls.routing_logic.keys())


@dataclass
class NavigationResult:
    """Represents the result of a navigation through the question tree.
    The Navigation Result can either be:
     - A QuestionForm, a WTForms form, which can be rendered with the question-page.html template
     - An internal redirect, an endpoint string processed with url_for during a request context
     - An external redirect, a Werkzeug response which can be returned from a request.
    """

    # The question form should be uninstantiated during traversal and only instantiated as part of handling the request
    question_form: type[QuestionForm] | None = None
    # Internal redirect is an endpoint string, which is evaluated during the request application context
    internal_redirect: str | None = None
    # Redirects the user to Check if you can get legal aid
    check_redirect: CheckRedirect | None = None

    @property
    def is_redirect(self) -> bool:
        """Indicates if navigation reached a final state (redirect or error)."""
        return bool(self.internal_redirect or self.check_redirect)


class CategoryTraversal:
    def __init__(self, initial_question: type[QuestionForm]):
        """Initialize with pre-calculated routes"""
        self.initial_routing_logic = initial_question.routing_logic
        # Dictionary to store all possible paths and their outcomes
        self.route_cache: dict[str, NavigationResult] = {
            "": NavigationResult(question_form=initial_question)
        }
        self._calculate_all_routes()

    def _calculate_all_routes(self) -> None:
        """Pre-calculate all possible routes during initialization"""

        def traverse_routing(node, current_path: list[str]) -> None:
            path_key = "/".join(current_path)
            # Stop if we hit a redirect or string endpoint
            if isinstance(node, CheckRedirect):
                self.route_cache[path_key] = NavigationResult(check_redirect=node)
                return
            if isinstance(node, str):
                self.route_cache[path_key] = NavigationResult(internal_redirect=node)
                return

            self.route_cache[path_key] = NavigationResult(question_form=node)
            # Continue traversing if this is a question form
            if hasattr(node, "routing_logic"):
                for choice, next_step in node.routing_logic.items():
                    traverse_routing(next_step, current_path + [choice])

        # Start traversal from each initial category
        for category, form in self.initial_routing_logic.items():
            traverse_routing(form, [category])

    def navigate_path(self, path: str) -> NavigationResult:
        """Navigate using pre-calculated routes.

        Raises:
            werkzeug.exceptions.NotFound if the path is invalid.
        """
        route = self.route_cache.get(path)

        if not route:
            raise NotFound()

        return route

    def get_question_answer_map(self, path: str) -> list[dict[str, str]]:
        """Create question-answer mapping using pre-calculated routes
        Returns a list of dictionaries mapping questions and answers.
        """
        result: list[dict[str, str]] = []

        if path == "":
            return result
        segments = path.split("/")

        current_path = ""

        for index, segment in enumerate(segments):
            route: NavigationResult = self.route_cache.get(current_path)

            if not route or not route.question_form:
                break

            if segment not in route.question_form.valid_choices():
                result.append(
                    {"question": route.question_form.title, "answer": "invalid choice"}
                )
                break

            if not hasattr(route.question_form, "title"):
                raise ValueError(f"{route.question_form} does not have a title")

            answer_label = route.question_form.get_choice_label(segment)
            result.append(
                {"question": route.question_form.title, "answer": answer_label}
            )
            current_path += segment if index == 0 else f"/{segment}"

        return result

    def get_all_valid_paths(self) -> list[str]:
        """Return a sorted list of all pre-calculated valid paths"""
        return sorted(list(self.route_cache.keys()))

    def get_previous_page_url(self, path: str) -> str:
        """Generate a URL for the previous question page.
            This populates the back button for each question page.

            If the previous page is a QuestionForm then previous_answer will be populated

        Args:
            path: Current URL path

        Returns:
            URL for the previous question page
        """
        path_segments = path.split("/")

        if len(path_segments) < 2:
            return url_for("categories.index")

        previous_answer = path_segments.pop()
        new_path = "/".join(path_segments)
        previous_page = self.navigate_path(new_path)

        return url_for(
            "categories.question_page",
            path=new_path,
            previous_answer=previous_answer
            if isinstance(previous_page, QuestionForm)
            else None,
        )

    def get_all_user_journeys(self) -> dict[str, NavigationResult]:
        """Generate dictionary of path components for the routing map debug page.
        Only includes paths that end in a redirect."""
        all_paths = self.get_all_valid_paths()

        full_paths = {}

        for path in all_paths:
            result = self.route_cache[path]
            if not result.is_redirect:
                continue
            full_paths[path] = result
        return full_paths

    def get_all_question_pages(self) -> dict[str, NavigationResult]:
        """Generate dictionary of path components for all question pages, for the accessibility tests
        Only includes paths that end on a question page."""
        all_paths = self.get_all_valid_paths()

        full_paths = {}

        for path in all_paths:
            result = self.route_cache[path]
            if result.is_redirect:
                continue
            full_paths[path] = result
        return full_paths


# Initialize the traversal system with the initial question
category_traversal = CategoryTraversal(initial_question=InitialCategoryQuestion)
