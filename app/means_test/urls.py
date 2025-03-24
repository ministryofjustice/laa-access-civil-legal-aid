from app.means_test.views import MeansTest, CheckYourAnswers, Ineligible
from app.means_test import bp, result

for name, form_class in MeansTest.forms.items():
    view_func = MeansTest.as_view(name, form_class, name)
    bp.add_url_rule(
        f"/{name}",
        view_func=view_func,
        methods=["GET", "POST"],
    )

bp.add_url_rule("/review", view_func=CheckYourAnswers.as_view("review"))
result.add_url_rule("/refer", view_func=Ineligible.as_view("ineligible"))
result.add_url_rule(
    "/hlpas", view_func=Ineligible.as_view("hlpas", template="means_test/hlpas.html")
)
