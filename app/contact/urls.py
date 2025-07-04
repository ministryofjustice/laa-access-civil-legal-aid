from app.contact.forms.check_your_answers import CheckYourAnswers
from app.contact.views import ContactView, CheckYourAnswersView
from app.contact import bp

for name, form_class in ContactView.forms.items():
    view_func = ContactView.as_view(name, form_class, name)
    bp.add_url_rule(
        f"/{getattr(form_class, 'url', name)}",
        view_func=view_func,
        methods=["GET", "POST"],
    )

bp.add_url_rule(
    "/check-you-answers", view_func=CheckYourAnswersView.as_view("review", CheckYourAnswers), methods=["GET", "POST"]
)
