from dataclasses import dataclass
from flask import url_for
from app.categories.constants import Category


@dataclass
class CategoryAnswer:
    question: str
    answer_value: str
    answer_label: str
    category: Category
    question_page: str
    next_page: str

    @property
    def edit_url(self):
        return url_for(self.question_page)

    @property
    def next_url(self):
        return url_for(self.next_page)
