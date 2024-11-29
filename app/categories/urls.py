from app.categories import bp
from app.categories.views import CategoryPage, IndexPage

bp.add_url_rule(
    "/", view_func=IndexPage.as_view("index", template="categories/index.html")
)
bp.add_url_rule(
    "/more-problems",
    view_func=CategoryPage.as_view(
        "more_problems", template="categories/more-problems.html"
    ),
)
