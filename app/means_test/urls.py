from app.categories.results.views import ResultPage
from app.means_test.views import MeansTest, CheckYourAnswers
from app.means_test import bp, result

for name, form_class in MeansTest.forms.items():
    view_func = MeansTest.as_view(name, form_class, name)
    bp.add_url_rule(
        f"/{name}",
        view_func=view_func,
        methods=["GET", "POST"],
    )

bp.add_url_rule("/review", view_func=CheckYourAnswers.as_view("review"))
result.add_url_rule(
    "/refer", view_func=ResultPage.as_view("ineligible", "means_test/refer.html")
)
result.add_url_rule(
    "/hlpas", view_func=ResultPage.as_view("hlpas", template="means_test/hlpas.html")
)
