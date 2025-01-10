from app.categories.forms import ChildInCareQuestionForm
from app.categories.x_cat.forms import AreYouUnder18Form
from app.categories.constants import EDUCATION


class SendChildInCareQuestionForm(ChildInCareQuestionForm):
    category = EDUCATION

    next_step_mapping = {
        "yes": "categories.send.age",
        "no": "categories.send.age",
    }


class SendAreYouUnder18Form(AreYouUnder18Form):
    category = EDUCATION
