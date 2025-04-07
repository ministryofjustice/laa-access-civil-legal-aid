from unittest.mock import patch

MOCK_LAALAA_RESULTS = {
    "count": 1,
    "results": [
        {
            "categories": ["COM"],
            "organisation": {"name": "Mock Organisation"},
            "location": {
                "address": "Address",
                "city": "",
                "postcode": "SW1A 1AA",
                "point": {"type": "Point", "coordinates": [1, 2]},
                "type": "Outreach Office",
            },
            "distance": 10,
        }
    ],
    "origin": {
        "postcode": "SW1A 0AA",
        "point": {"type": "Point", "coordinates": [1, 2]},
    },
}


class TestFindALegalAdviser:
    def test_result_page_with_single_category(self, app, client):
        postcode = "SW1A 1AA"
        category = "COM"
        page_num = 1
        postcode_region = "London"

        with patch(
            "app.find_a_legal_adviser.routes.laalaa_search",
            return_value=MOCK_LAALAA_RESULTS,
        ) as mock_laalaa_search:
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
                categories=[category],
                page=page_num,
            )

    def test_result_page_with_secondary_category(self, app, client):
        postcode = "SW1A 1AA"
        category = "COM"
        secondary_category = "MHE"
        page_num = 1

        with patch(
            "app.find_a_legal_adviser.routes.laalaa_search",
            return_value=MOCK_LAALAA_RESULTS,
        ) as mock_laalaa_search:
            response = client.get(
                "/find-a-legal-adviser",
                query_string={
                    "category": category,
                    "secondary_category": secondary_category,
                    "postcode": postcode,
                    "page": page_num,
                },
            )

            assert response.status_code == 200
            assert response.request.path == "/find-a-legal-adviser"
            mock_laalaa_search.assert_called_with(
                postcode=postcode,
                categories=[
                    category,
                    secondary_category,
                ],
                page=page_num,
            )

    @patch("app.find_a_legal_adviser.routes.render_template")
    def test_result_page_with_no_category(self, app, client):
        postcode = "SW1A 1AA"

        with patch(
            "app.find_a_legal_adviser.routes.laalaa_search",
            return_value=MOCK_LAALAA_RESULTS,
        ) as mock_laalaa_search:
            client.get(
                "/find-a-legal-adviser",
                query_string={
                    "postcode": postcode,
                    "page": 1,
                },
            )

            mock_laalaa_search.assert_called_with(
                postcode=postcode,
                categories=[],
                page=1,
            )

    @patch("app.find_a_legal_adviser.routes.render_template")
    def test_result_page_with_only_secondary_category(self, app, client):
        postcode = "SW1A 1AA"
        secondary_category = "MHE"

        with patch(
            "app.find_a_legal_adviser.routes.laalaa_search",
            return_value=MOCK_LAALAA_RESULTS,
        ) as mock_laalaa_search:
            client.get(
                "/find-a-legal-adviser",
                query_string={
                    "postcode": postcode,
                    "secondary_category": secondary_category,
                    "page": 1,
                },
            )

            mock_laalaa_search.assert_called_with(
                postcode=postcode,
                categories=["MHE"],
                page=1,
            )

    @patch("app.find_a_legal_adviser.routes.render_template")
    def test_result_page_with_invalid_categories(self, app, client):
        postcode = "SW1A 1AA"
        category = "invalid"
        secondary_category = "category"

        with patch(
            "app.find_a_legal_adviser.routes.laalaa_search",
            return_value=MOCK_LAALAA_RESULTS,
        ) as mock_laalaa_search:
            client.get(
                "/find-a-legal-adviser",
                query_string={
                    "postcode": postcode,
                    "category": category,
                    "secondary_category": secondary_category,
                },
            )

            mock_laalaa_search.assert_called_with(
                postcode=postcode,
                categories=[],
                page=1,
            )
