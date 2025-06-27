from app.contact.views import ContactView
from app.contact import bp

for name, form_class in ContactView.forms.items():
    view_func = ContactView.as_view(name, form_class, name)
    bp.add_url_rule(
        f"/contact-us/{name}",
        view_func=view_func,
        methods=["GET", "POST"],
    )
