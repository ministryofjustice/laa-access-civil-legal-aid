from flask import redirect, url_for, abort
from app.categories.questions.discrimination import DiscriminationWhereForm
from app.categories.questions.domestic_abuse import DomesticAbuseTraversal
from werkzeug.wrappers.response import Response
from app.categories.forms import QuestionForm


class CategoryTraversal:
    #  Maps each category to the first question
    #  This can either be a QuestionForm or an endpoint string
    routing_logic = {
        "discrimination": DiscriminationWhereForm,
        "domestic-abuse": DomesticAbuseTraversal,
        "clinical-negligence": redirect(
            "http://127.0.0.1:5000/scope/refer/legal-adviser?category=clinneg"
        ),
    }

    def get_onward_question_from_path(self, path: str) -> QuestionForm | Response:
        """Takes in the users URL endpoint as a path and returns either an onward question form or a response.
        If a response is returned then the user has concluded the category diagnosis and should be directed to the
        onward page.

        If an

        :param path: Full endpoint path i.e. "discrimination/work/age"
        :return: QuestionForm or a HTTP Response
        """
        path = path.split("/")

        if len(path) == 0:
            return redirect(url_for("categories.index"))

        if path[0] not in self.routing_logic:
            return abort(404)
        category = path[0]
        question_form: QuestionForm = self.routing_logic[category]

        if isinstance(question_form, str):
            return redirect(url_for(question_form))

        # Traverse down the diagnosis tree
        # If an invalid category value is found then stop
        for node in path[
            1:
        ]:  # Start iterating from the 2nd element as the category is the first
            if node not in question_form.valid_choices():
                return question_form
            if node not in question_form.routing_logic:
                if "default" not in question_form.routing_logic:
                    return redirect(
                        url_for("categories.index")
                    )  # If the answer isn't valid then stop
                node = "default"

            next_page: QuestionForm | str = question_form.routing_logic[node]

            if isinstance(next_page, Response):
                return next_page

            # If the next page is not a question we are at the end of the tree and want to show the user an onward page
            if isinstance(next_page, str):
                return redirect(url_for(next_page))

            question_form = next_page

        return question_form

    def get_question_answer_map_from_path(self, path: str) -> dict:
        path = path.split("/")
        question_map = {}

        routing_logic = self.routing_logic
        question_form = InitialCategoryQuestion()
        for node in path:
            if node not in question_form.valid_choices():
                print(question_map)
                return question_map

            question_map[question_form.title] = node

            if node not in routing_logic:
                node = "default"

            question_form = routing_logic[node]
            if not issubclass(question_form, QuestionForm):
                return question_map

            # Change the routing logic in the next iteration to be that of the current question
            routing_logic = question_form.routing_logic

        return question_map

    @classmethod
    def map_routing_logic(cls):
        """Recursively maps the routing logic relationships between the categories of law.

        Returns:
            dict: A nested dictionary representing the complete routing structure
        """

        def get_class_name(cls):
            return cls.__name__ if hasattr(cls, "__name__") else str(cls)

        def traverse_class(cls, visited=None):
            if visited is None:
                visited = set()

            class_name = get_class_name(cls)

            # Prevent infinite recursion
            if class_name in visited:
                return f"Circular reference to {class_name}"

            visited.add(class_name)

            # If class has no routing_logic attribute, return None
            if not hasattr(cls, "routing_logic"):
                return None

            result = {}

            for key, value in cls.routing_logic.items():
                if isinstance(value, Response):
                    result[key] = f"redirect: {value.headers['location']}"
                elif isinstance(value, str):
                    result[key] = value
                else:
                    # Recursively map the nested class
                    nested_map = traverse_class(value, visited.copy())
                    result[key] = {get_class_name(value): nested_map}

            return result

        return {get_class_name(cls): traverse_class(cls)}

    @staticmethod
    def get_previous_page_from_path(path: str) -> str:
        path = path.split("/")

        if len(path) < 2:
            return url_for("categories.index")

        previous_answer = path.pop(-1)
        new_path = "/".join(path)
        return url_for(
            "categories.question_page", path=new_path, previous_answer=previous_answer
        )


category_traversal = CategoryTraversal()


class InitialCategoryQuestion(QuestionForm):
    title = "Choose the problem you need help with."

    @classmethod
    def valid_choices(cls):
        return [route for route in CategoryTraversal.routing_logic]
