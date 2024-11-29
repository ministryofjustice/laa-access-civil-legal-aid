from app.categories.views import CategoryPage
from flask import session, redirect, url_for


class HlpasInScopePage(CategoryPage):
    def dispatch_request(self):
        session["hlpas_eligible"] = True
        return redirect(url_for("categories.results.in_scope"))
