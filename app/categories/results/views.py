from app.categories.constants import Category
from app.categories.views import CategoryPage
from flask import session, redirect, url_for, render_template
from app.find_a_legal_adviser.laalaa import get_category_code as get_fala_category_code
from app.api import cla_backend


class HlpasInScopePage(CategoryPage):
    def dispatch_request(self):
        session["hlpas_eligible"] = True
        return redirect(url_for("categories.results.in_scope"))


class ResultPage(CategoryPage):
    def __init__(self, template, get_help_organisations: bool = True, *args, **kwargs):
        super().__init__(template, *args, **kwargs)
        self.get_help_organisations = get_help_organisations

    def get_context(self, category: Category = None):
        article_category_name = (
            category.article_category_name
            if isinstance(category, Category)
            else "other"
        )
        organisations = (
            cla_backend.get_help_organisations(article_category_name)
            if article_category_name and self.get_help_organisations
            else []
        )
        return {
            "category_name": category.referrer_text
            if isinstance(category, Category)
            else None,
            "organisations": organisations,
            "fala_category_code": get_fala_category_code(article_category_name),
        }

    def dispatch_request(self):
        return render_template(self.template, **self.get_context(session.category))


class OutOfScopePage(ResultPage):
    """Out of scope pages get the category information from the URL/ View rather than the session.
    This allows them to be linked to without having to go through the journey.
    """

    def __init__(self, template, category: Category | None = None, *args, **kwargs):
        super().__init__(template, *args, **kwargs)
        self.category = category

    def dispatch_request(self):
        """Gets the category from the view (url) rather than the session."""
        return render_template(self.template, **self.get_context(self.category))


class CannotFindYourProblemPage(OutOfScopePage):
    template = "categories/cannot-find-problem.html"

    def __init__(self, next_steps_page: str = None, *args, **kwargs):
        kwargs["get_help_organisations"] = (
            False  # Disables fetching help orgs from backend as this page doesn't require it.
        )
        kwargs["template"] = self.template
        super().__init__(*args, **kwargs)
        if next_steps_page is None:
            next_steps_page = "categories.results.next_steps"
        self.next_steps_page = next_steps_page

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context.update(
            {
                "next_steps_page": self.next_steps_page,
            }
        )
        return context


class NextStepsPage(OutOfScopePage):
    template: str = "categories/next-steps.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, self.template, **kwargs)
