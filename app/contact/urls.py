from app.contact import bp
from app.categories.views import CategoryPage

bp.add_url_rule(
    "/contact",
    view_func=CategoryPage.as_view("contact", template="contact/contact.html"),
)
