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
