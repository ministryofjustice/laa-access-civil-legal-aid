from app.categories.forms import ChildInCareQuestionForm
from app.categories.constants import Category


class SendChildInCareQuestionForm(ChildInCareQuestionForm):
    category = Category.EDUCATION
