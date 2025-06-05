from unittest.mock import patch

import pytest
from app.find_a_legal_adviser.fala import create_fala_url


class TestCreateFALARedirect:
    @pytest.mark.parametrize(
        "category, secondary_category, expected_url",
        [
            # Test with default endpoint but different parameters
            (None, None, "https://staging.find-legal-advice.justice.gov.uk/check"),
            (
                "hou",
                None,
                "https://staging.find-legal-advice.justice.gov.uk/check?categories=hou",
            ),
            (
                "hou",
                "immas",
                "https://staging.find-legal-advice.justice.gov.uk/check?categories=hou&sub-category=immas",
            ),
            # Test with different endpoint and parameters
            (
                "hlpas",
                None,
                "https://staging.find-legal-advice.justice.gov.uk/check?categories=hlpas",
            ),
            (
                "hlpas",
                "mat",
                "https://staging.find-legal-advice.justice.gov.uk/check?categories=hlpas&sub-category=mat",
            ),
            # Test case where category is None but secondary_category is provided (should ignore secondary)
            (None, "ignored", "https://staging.find-legal-advice.justice.gov.uk/check"),
        ],
    )
    def test_create_fala_url_with_parameters(
        self, app, client, category, secondary_category, expected_url
    ):
        with client.application.test_request_context("/"):
            result = create_fala_url(
                category=category, secondary_category=secondary_category
            )
            assert result == expected_url

    def test_create_fala_url_without_trailing_slash(self, app, client):
        app.config["FALA_URL"] = "https://find-legal-advice.justice.gov.uk/"

        with client.application.test_request_context("/"):
            result = create_fala_url()
            assert result == "https://find-legal-advice.justice.gov.uk/check"

    def test_create_fala_url_no_config(self, app, client):
        if "FALA_URL" in app.config:
            del app.config["FALA_URL"]

        with client.application.test_request_context("/"):
            with pytest.raises(KeyError) as excinfo:
                create_fala_url()

            assert "FALA_URL not configured" in str(excinfo.value)


class TestFindALegalAdviserRedirect:
    def test_redirect(self, app, client):
        """
        Test that create_fala_url and render_template are called with valid categories
        """
        category = "hou"
        secondary_category = "immas"

        with patch(
            "app.find_a_legal_adviser.routes.create_fala_url"
        ) as mock_create_fala_url:
            mock_create_fala_url.return_value = "https://staging.find-legal-advice.justice.gov.uk/check?categories=housing&sub-category=eviction"

            with patch(
                "app.find_a_legal_adviser.routes.render_template"
            ) as mock_render_template:
                response = client.get(
                    "/find-a-legal-adviser",
                    query_string={
                        "category": category,
                        "secondary_category": secondary_category,
                    },
                )

                assert response.status_code == 200

                mock_create_fala_url.assert_called_once_with(
                    category=category, secondary_category=secondary_category
                )

                mock_render_template.assert_called_once_with(
                    "categories/fala-interstitial.html",
                    fala_url="https://staging.find-legal-advice.justice.gov.uk/check?categories=housing&sub-category=eviction",
                )

    def test_redirect_with_invalid_categories(self, app, client):
        """
        Test that invalid categories are not passed to create_fala_url
        """
        with patch(
            "app.find_a_legal_adviser.routes.create_fala_url"
        ) as mock_create_fala_url:
            mock_create_fala_url.return_value = (
                "https://staging.find-legal-advice.justice.gov.uk/check"
            )

            with patch("app.find_a_legal_adviser.routes.abort") as mock_abort:
                client.get(
                    "/find-a-legal-adviser",
                    query_string={
                        "category": "invalid",
                        "secondary_category": "also-invalid",
                    },
                )

                mock_create_fala_url.assert_not_called()

                mock_abort.assert_called_once()

    def test_redirect_with_mixed_valid_invalid_categories(self, app, client):
        """
        Test handling of mixed valid and invalid categories
        """
        valid_category = "housing"
        invalid_category = "invalid"

        with patch(
            "app.find_a_legal_adviser.routes.create_fala_url"
        ) as mock_create_fala_url:
            mock_create_fala_url.return_value = "https://staging.find-legal-advice.justice.gov.uk/check?categories=housing"

            with patch("app.find_a_legal_adviser.routes.abort") as mock_abort:
                client.get(
                    "/find-a-legal-adviser",
                    query_string={
                        "category": valid_category,
                        "secondary_category": invalid_category,
                    },
                )

                mock_create_fala_url.assert_not_called()

                mock_abort.assert_called_once()
