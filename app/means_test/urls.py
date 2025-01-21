from app.means_test.views import MeansTest, CheckYourAnswers
from app.means_test import bp

for name, form_class in MeansTest.forms.items():
    view_func = MeansTest.as_view(name, form_class, name)
    bp.add_url_rule(
        f"/{name}",
        view_func=MeansTest.as_view(name, form_class, name),
        methods=["GET", "POST"],
    )

bp.add_url_rule("/review", view_func=CheckYourAnswers.as_view("review"))
