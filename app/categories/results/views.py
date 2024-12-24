from app.categories.results.help_organisations import get_help_organisations
from app.categories.views import CategoryPage
from flask import session, redirect, url_for, render_template
from app.find_a_legal_adviser.laalaa import get_category_code as get_fala_category_code


class HlpasInScopePage(CategoryPage):
    def dispatch_request(self):
        session["hlpas_eligible"] = True
        return redirect(url_for("categories.results.in_scope"))


class ResultPage(CategoryPage):
    @staticmethod
    def get_context():
        category = session.get("category")
        organisations = get_help_organisations(category)
        return {
            "category_name": category,
            "organisations": organisations,
            "fala_category_code": get_fala_category_code(category),
        }

    def dispatch_request(self):
        return render_template(self.template, **self.get_context())
