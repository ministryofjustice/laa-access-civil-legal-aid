from flask.views import View
from flask import render_template, redirect, url_for, session, request
from app.categories.forms import QuestionForm
from app.categories.utils import get_items_with_divisor, check_radio_field
from app.session import set_category_question_answer, get_category_question_answer


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
    pass


class QuestionPage(View):
    """Base question page view that all category question pages should inherit from.
    Responsible for rendering the question page, handling the form submission and saving the users answers to their session.
    """

    form = QuestionForm

    methods = ["GET", "POST"]

    def __init__(self, form):
        self.form = form

    def get_next_page(self, answer):
        return redirect(url_for(self.form.next_step_mapping[answer]))

    def update_session(self, answer: str = None):
        session["previous_page"] = request.endpoint
        set_category_question_answer(self.form.title, answer, self.form.category)

    def dispatch_request(self):
        form = self.form(request.args)

        items = None
        if form.show_or_divisor:
            items = get_items_with_divisor(form.question.choices)

        previous_answer = get_category_question_answer(form)

        if previous_answer:
            items = check_radio_field(form.question, previous_answer, items)

        if "submit" in request.args and form.validate():
            self.update_session(form.question.data)
            return self.get_next_page(form.question.data)

        return render_template(
            "categories/question-page.html",
            form=form,
            items=items,
        )
