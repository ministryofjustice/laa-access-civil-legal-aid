from unittest.mock import patch


def test_result_page_with_single_category(app):
    # Result page data
    postcode = "SW1A 1AA"
    category = "COM"
    page_num = 1
    postcode_region = "London"

    # laalaa_search results
    mock_results = {
        "count": 1,
        "results": [
            {"categories": ["COM"], "organisation": {"name": "Mock Organisation"}}
        ],
    }

    # Mocks laalaa_search
    with patch(
        "app.find_a_legal_advisor.laalaa.laalaa_search", return_value=mock_results
    ):
        # Mocks results page
        with app.test_client() as client:
            response = client.get(
                "/find-a-legal-advisor",
                query_string={
                    "category": category,
                    "postcode": postcode,
                    "page": page_num,
                    "postcode_region": postcode_region,
                },
            )

        assert response.status_code == 200
        assert response.request.path == "/find-a-legal-advisor"


def test_result_page_with_secondary_category(app):
    # Result page data
    postcode = "SW1A 1AA"
    category = "COM"
    secondary_category = "HLE"
    page_num = 1
    postcode_region = "London"

    # laalaa_search results
    mock_results = {
        "count": 1,
        "results": [
            {
                "categories": ["COM", "HLE"],
                "organisation": {"name": "Mock Organisation"},
            }
        ],
    }

    # Mocks laalaa_search
    with patch(
        "app.find_a_legal_advisor.laalaa.laalaa_search", return_value=mock_results
    ):
        # Mocks results page
        with app.test_client() as client:
            response = client.get(
                "/find-a-legal-advisor",
                query_string={
                    "category": category,
                    "secondary_category": secondary_category,
                    "postcode": postcode,
                    "page": page_num,
                    "postcode_region": postcode_region,
                },
            )

        assert response.status_code == 200
        assert response.request.path == "/find-a-legal-advisor"
