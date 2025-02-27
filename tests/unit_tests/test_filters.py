from app.main.filters import category_url_for


def test_filter_category_url(app):
    with app.app_context():
        # url is a string
        assert category_url_for("categories.index") == "/find-your-problem"
        endpoint = {
            "endpoint": "find-a-legal-adviser.search",
            "category": "mhe",
            "secondary_category": "com",
        }
        # url is a dict
        assert (
            category_url_for(endpoint)
            == "/find-a-legal-adviser?category=mhe&secondary_category=com"
        )

        # url is invalid(missing endpoint)
        endpoint = {
            "category": "mhe",
            "secondary_category": "com",
        }
        try:
            category_url_for(endpoint)
            assert False, "Expecting exception for invalid url"
        except ValueError:
            pass
