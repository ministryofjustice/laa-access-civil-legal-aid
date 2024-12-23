from app.categories.results.help_organisations import get_help_organisations
from app.categories.views import CategoryPage
from flask import session, redirect, url_for, render_template


class HlpasInScopePage(CategoryPage):
    def dispatch_request(self):
        session["hlpas_eligible"] = True
        return redirect(url_for("categories.results.in_scope"))


class ResultPage(CategoryPage):
    @staticmethod
    def get_context():
        return {
            "category_name": session.get("category"),
            "hlpas_eligible": session.get("hlpas_eligible"),
        }

    def dispatch_request(self):
        category = session.get("category")
        organisations = get_help_organisations(
            article_category__name=category.capitalize()
        )
        print(organisations)
        return render_template(
            self.template, category_name=category, organisations=organisations
        )
