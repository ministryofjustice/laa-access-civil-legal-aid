from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from flask import url_for
from flask_babel import LazyString

from app.categories.constants import Category


class QuestionType(str, Enum):
    CATEGORY = "category"
    SUB_CATEGORY = "sub_category"
    ONWARD = "onward_question"


@dataclass
class CategoryAnswer:
    question: str
    answer_value: str
    answer_label: str | LazyString
    category: Category
    question_page: str
    next_page: str
    question_type: Optional[QuestionType] = field(default=QuestionType.SUB_CATEGORY)

    @property
    def edit_url(self):
        return url_for(self.question_page)

    @property
    def next_url(self):
        return url_for(self.next_page)

    @property
    def question_type_is_sub_category(self):
        return self.question_type == QuestionType.SUB_CATEGORY

    @property
    def question_type_is_onward(self):
        return self.question_type == QuestionType.ONWARD
