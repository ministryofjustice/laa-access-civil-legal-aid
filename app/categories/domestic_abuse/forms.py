from app.categories.forms import SafeguardingQuestionForm
from app.categories.constants import DOMESTIC_ABUSE


class WorriedAboutSomeonesSafetyForm(SafeguardingQuestionForm):
    category = DOMESTIC_ABUSE
