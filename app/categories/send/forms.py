from app.categories.forms import ChildInCareQuestionForm
from app.categories.categories import Category


class SendChildInCareQuestionForm(ChildInCareQuestionForm):
    category = Category.SEND
