from app.categories.forms import ChildInCareQuestionForm
from app.categories.x_cat.forms import AreYouUnder18Form


class SendChildInCareQuestionForm(ChildInCareQuestionForm):
    category = "SEND"

    next_step_mapping = {
        "yes": "categories.send.age",
        "no": "categories.send.age",
    }


class SendAreYouUnder18Form(AreYouUnder18Form):
    category = "SEND"
