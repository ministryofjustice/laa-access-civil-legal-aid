from app.categories.forms import ChildInCareQuestionForm
from app.categories.constants import EDUCATION


class SendChildInCareQuestionForm(ChildInCareQuestionForm):
    category = EDUCATION.sub.tribunals
