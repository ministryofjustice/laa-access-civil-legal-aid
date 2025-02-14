from flask.sansio.blueprints import Blueprint
from flask.views import View
from flask import render_template, redirect, url_for, session, request
from app.categories.forms import QuestionForm
from app.categories.constants import Category


class CategoryPage(View):
    template: str = None
    question_title: str = ""
    category: Category

    def __init__(self, template, *args, **kwargs):
        self.template = template

    def update_session(self, question: str, answer: str, category: Category) -> None:
        """
        Update the session with the current page and answer.

        """
        session.set_category_question_answer(
            question_title=question,
            answer=answer,
            category=category,
        )

    def dispatch_request(self):
        category = getattr(self, "category", None)
        if category is not None:
            session["category"] = category

        response = self.process_request()
        if not response:
            response = render_template(self.template)
        return response

    def process_request(self):
        return None


class IndexPage(CategoryPage):
    def dispatch_request(self):
        session.clear()
        return render_template(self.template)


class CategoryLandingPage(CategoryPage):
    template: str = "categories/landing.html"

    routing_map: dict[str, str] = {}

    def process_request(self):
        return render_template(
            self.template, category=self.category, routing_map=self.routing_map
        )

    @classmethod
    def register_routes(cls, blueprint: Blueprint):
        for answer, next_page in cls.routing_map.items():
            blueprint.add_url_rule(
                f"/{cls.category}/{answer}",
                view_func=CategoryAnswerPage.as_view(
                    answer,
                    question=cls.question_title,
                    answer=answer,
                    next_page=next_page,
                    category=cls.category,
                ),
            )

    @classmethod
    def register_routes_2(cls, blueprint: Blueprint, path: str = None):
        if not path:
            path = cls.category.code.lower().replace("_", "-")

        blueprint.add_url_rule(
            f"/{path}/",
            view_func=cls.as_view("landing", template=cls.template),
        )
        cls.register_sub_routes(blueprint, path, cls.routing_map["main"])
        cls.register_sub_routes(blueprint, path, cls.routing_map["more"])

        if "other" in cls.routing_map and cls.routing_map["other"] is not None:
            blueprint.add_url_rule(
                f"/{path}/answer/other",
                view_func=CategoryAnswerPage.as_view(
                    "other",
                    question=cls.question_title,
                    answer="other",
                    next_page=cls.routing_map["other"],
                    category=cls.category,
                ),
            )

    @classmethod
    def register_sub_routes(cls, blueprint: Blueprint, path, routes):
        for sub_category, next_page in routes:
            blueprint.add_url_rule(
                f"/{path}/answer/{sub_category.code.replace('_', '-')}",
                view_func=CategoryAnswerPage.as_view(
                    sub_category.code,
                    question=cls.question_title,
                    answer=sub_category.code,
                    next_page=next_page,
                    category=sub_category,
                ),
            )


class CategoryAnswerPage(View):
    def __init__(self, question, answer, next_page, category):
        self.question = question
        self.answer = answer
        self.next_page = next_page
        self.category = category

    def update_session(self) -> None:
        """
        Update the session with the current page and answer.

        """
        session["previous_page"] = request.endpoint
        session.set_category_question_answer(
            question_title=self.question,
            answer=self.answer,
            category=self.category,
        )

    def dispatch_request(self):
        self.update_session()
        if isinstance(self.next_page, dict):
            return redirect(url_for(**self.next_page))
        return redirect(url_for(self.next_page))


class QuestionPage(CategoryPage):
    """Base view for handling question pages with form submission and session management.

    This view handles:
    - Rendering the question page
    - Processing form submissions
    - Managing user session data
    - Routing to the next appropriate page
    """

    template: str = "categories/question-page.html"
    form_class: type[QuestionForm] | None = None

    def __init__(self, form_class: type[QuestionForm], template=None):
        """Initialize the view with a form class.

        Args:
            form_class: The WTForms form class to use for this question page
            template: The template to use for this question page
        """
        self.form_class = form_class
        self.template = template or self.template
        self.category = form_class.category
        super().__init__(self.template)

    def get_next_page(self, answer: str) -> redirect:
        """Determine and redirect to the next page based on the user's answer.

        Args:
            answer: The user's selected answer

        Returns:
            A Flask redirect response to the next appropriate page

        Raises:
            ValueError if the answer does not have a mapping to a next page
        """
        optional_answers = [
            "notsure",
            "none",
        ]  # We should only route to these pages if they are the only answer

        if len(answer) == 1 and answer[0] in optional_answers:
            return redirect(url_for(self.form_class.next_step_mapping[answer[0]]))

        if isinstance(answer, list):
            for a in answer:
                if a in self.form_class.next_step_mapping and a not in optional_answers:
                    return redirect(url_for(self.form_class.next_step_mapping[a]))
            answer = "*"

        if answer not in self.form_class.next_step_mapping:
            raise ValueError(f"No mapping found for answer: {answer}")

        next_page = self.form_class.next_step_mapping[answer]
        if isinstance(next_page, dict):
            return redirect(url_for(**next_page))
        return redirect(url_for(next_page))

    def process_request(self):
        """Handle requests for the question page, including form submissions.

        This method processes both initial page loads and form submissions,
        which are differentiated by the presence of a 'submit' parameter
        in the query string.

        Returns:
            Either a redirect to the next page or the rendered template
        """
        form = self.form_class(request.args)
        session["category"] = form.category

        if form.submit.data and form.validate():
            self.update_session(
                question=form.title, answer=form.question.data, category=form.category
            )
            return self.get_next_page(form.question.data)

        # Pre-populate form with previous answer if it exists
        previous_answer = session.get_category_question_answer(form.title)
        if previous_answer:
            form.question.data = previous_answer

        return render_template(
            self.template,
            form=form,
        )
