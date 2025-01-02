from app.categories.forms import SafeguardingQuestionForm
from app.categories.categories import Category


class WorriedAboutSomeonesSafetyForm(SafeguardingQuestionForm):
    category = Category.DOMESTIC_ABUSE
