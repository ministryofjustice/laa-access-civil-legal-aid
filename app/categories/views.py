from flask.sansio.blueprints import Blueprint
from flask.views import View
from flask import render_template, redirect, url_for, session, request
from app.categories.forms import QuestionForm
from app.categories.constants import Category


class CategoryPage(View):
    template: str = None

    def __init__(self, template, *args, **kwargs):
        self.template = template

    def dispatch_request(self):
        return render_template(self.template)


class IndexPage(CategoryPage):
    def dispatch_request(self):
        session.clear()
        return render_template(self.template)


class CategoryLandingPage(CategoryPage):
    question_title: str = ""

    routing_map: dict[str, str] = {}

    category: Category

    def dispatch_request(self):
        return render_template(self.template, category=self.category)

    @classmethod
    def register_routes(cls, blueprint: Blueprint):
        for answer, next_page in cls.routing_map.items():
            blueprint.add_url_rule(
                f"/{cls.category.code}/{answer}",
                view_func=CategoryAnswerPage.as_view(
                    answer,
                    question=cls.question_title,
                    answer=answer,
                    next_page=next_page,
                    category=cls.category,
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


class QuestionPage(View):
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

    def update_session(self, answer: str | None = None) -> None:
        """
        Update the session with the current page and answer.

        Args:
            answer: The user's selected answer
        """
        session["previous_page"] = request.endpoint
        session.set_category_question_answer(
            question_title=self.form_class.title,
            answer=answer,
            category=self.form_class.category,
        )

    def dispatch_request(self):
        """Handle requests for the question page, including form submissions.

        This method processes both initial page loads and form submissions,
        which are differentiated by the presence of a 'submit' parameter
        in the query string.

        Returns:
            Either a redirect to the next page or the rendered template
        """
        form = self.form_class(request.args)

        if form.submit.data and form.validate():
            self.update_session(form.question.data)
            return self.get_next_page(form.question.data)

        # Pre-populate form with previous answer if it exists
        previous_answer = session.get_category_question_answer(form.title)
        if previous_answer:
            form.question.data = previous_answer

        return render_template(
            self.template,
            form=form,
        )
