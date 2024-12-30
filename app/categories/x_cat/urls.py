from app.categories.x_cat import bp
from app.categories.views import QuestionPage
from app.categories.x_cat.forms import AntiSocialBehaviourForm

bp.add_url_rule(
    "/landlord-council",
    view_func=QuestionPage.as_view(
        "landlord-council",
        form_class=AntiSocialBehaviourForm,
        template="categories/public/reason.html",  # TODO: Update this to use a caption question template if we decide to standardise on this
    ),
)
