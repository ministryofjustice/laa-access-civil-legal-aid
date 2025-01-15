import pytest
from unittest.mock import Mock

from app.means_test.views import MeansTest


@pytest.fixture
def means_test():
    """Creates a MeansTest with 4 pages that are all shown by default"""

    test = MeansTest(Mock(), "mock-page")
    test.forms = {
        "page1": ShownForm,
        "page2": ShownForm,
        "page3": ShownForm,
        "page4": ShownForm,
    }
    return test


class ShownForm:
    @classmethod
    def should_show(cls):
        return True


class SkippedForm:
    @classmethod
    def should_show(cls):
        return False


def test_returns_next_page(means_test):
    assert means_test.get_next_page("page1") == "page2"
    assert means_test.get_next_page("page2") == "page3"
    assert means_test.get_next_page("page3") == "page4"
    assert means_test.get_next_page("page4") == "review"


def test_skips_hidden_page(means_test):
    means_test.forms["page2"] = SkippedForm
    assert means_test.get_next_page("page1") == "page3"


def test_skips_multiple_hidden_pages(means_test):
    means_test.forms["page2"] = SkippedForm
    means_test.forms["page3"] = SkippedForm
    assert means_test.get_next_page("page1") == "page4"


def test_returns_review_when_all_remaining_hidden(means_test):
    means_test.forms["page2"] = SkippedForm
    means_test.forms["page3"] = SkippedForm
    means_test.forms["page4"] = SkippedForm
    assert means_test.get_next_page("page1") == "review"


def test_returns_review_for_invalid_page(means_test):
    assert means_test.get_next_page("non_existent_page") == "review"
