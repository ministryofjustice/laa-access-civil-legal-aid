from app.means_test.views import MeansTest, CheckYourAnswers
from app.means_test import bp
from app.contact.views import ContactUs

for name, form_class in MeansTest.forms.items():
    view_func = MeansTest.as_view(name, form_class, name)
    bp.add_url_rule(
        f"/{name}",
        view_func=view_func,
        methods=["GET", "POST"],
    )

bp.add_url_rule("/review", view_func=CheckYourAnswers.as_view("review"))
bp.add_url_rule(
    "/eligible",
    view_func=ContactUs.as_view(
        "eligible", template="contact/eligible.html", attach_eligiblity_data=True
    ),
)
