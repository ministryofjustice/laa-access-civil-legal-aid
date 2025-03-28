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
        "results": [{"categories": ["COM"], "organisation": {"name": "Mock Organisation"}}],
    }

    # Mocks laalaa_search
    with patch("app.find_a_legal_adviser.laalaa.laalaa_search", return_value=mock_results) as mock_laalaa_search:
        mock_laalaa_search(postcode=postcode, categories=[category], page=page_num)
        # Mocks results page
        with app.test_client() as client:
            response = client.get(
                "/find-a-legal-adviser",
                query_string={
                    "category": category,
                    "postcode": postcode,
                    "page": page_num,
                    "postcode_region": postcode_region,
                },
            )

        assert response.status_code == 200
        assert response.request.path == "/find-a-legal-adviser"
        mock_laalaa_search.assert_called_with(
            postcode=postcode,
            categories=[category],  # Verify the categories parameter
            page=page_num,
        )


def test_result_page_with_secondary_category(app):
    # Result page data
    postcode = "SW1A 1AA"
    category = "COM"
    secondary_category = "MHE"
    page_num = 1
    postcode_region = "London"

    # laalaa_search results
    mock_results = {
        "count": 1,
        "results": [
            {
                "categories": ["COM", "MHE"],
                "organisation": {"name": "Mock Organisation"},
            }
        ],
    }

    # Mocks laalaa_search
    with patch("app.find_a_legal_adviser.laalaa.laalaa_search", return_value=mock_results) as mock_laalaa_search:
        mock_laalaa_search(postcode=postcode, categories=[category, secondary_category], page=page_num)
        # Mocks results page
        with app.test_client() as client:
            response = client.get(
                "/find-a-legal-adviser",
                query_string={
                    "category": category,
                    "secondary_category": secondary_category,
                    "postcode": postcode,
                    "page": page_num,
                    "postcode_region": postcode_region,
                },
            )

        assert response.status_code == 200
        assert response.request.path == "/find-a-legal-adviser"
        mock_laalaa_search.assert_called_with(
            postcode=postcode,
            categories=[
                category,
                secondary_category,
            ],  # Verify the categories parameter
            page=page_num,
        )
