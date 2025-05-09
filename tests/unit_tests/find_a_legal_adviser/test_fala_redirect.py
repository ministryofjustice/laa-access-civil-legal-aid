from unittest.mock import patch

import pytest
from app.find_a_legal_adviser.fala import kwargs_to_urlparams, create_fala_url


class TestUrlHelpers:
    @pytest.mark.parametrize(
        "kwargs, expected_result",
        [
            ({"param1": "value1"}, "param1=value1"),
            ({"param1": "value1", "param2": "value2"}, "param1=value1&param2=value2"),
            ({"param": "value with spaces"}, "param=value+with+spaces"),
            ({"param": "special/chars?&="}, "param=special%2Fchars%3F%26%3D"),
            ({"param1": "value1", "param2": None}, "param1=value1"),
            ({}, ""),
            ({"empty": ""}, "empty="),
            (
                {"list_param": ["value1", "value2"]},
                "list_param=value1&list_param=value2",
            ),
        ],
    )
    def test_kwargs_to_urlparams(self, kwargs, expected_result):
        """Test that kwargs_to_urlparams correctly converts kwargs to URL parameters."""
        result = kwargs_to_urlparams(**kwargs)
        assert result == expected_result

    def test_kwargs_to_urlparams_all_none(self):
        """Test that kwargs_to_urlparams returns an empty string when all values are None."""
        result = kwargs_to_urlparams(param1=None, param2=None)
        assert result == ""

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
    def test_redirect_with_feature_flag_enabled(self, app, client):
        """
        Test that create_fala_url and render_template are called
        when the feature flag is enabled with valid categories
        """
        app.config["REDIRECT_FALA_REQUESTS"] = True

        category = "hou"
        secondary_category = "immas"

        with patch(
            "app.find_a_legal_adviser.routes.is_valid_category_code"
        ) as mock_is_valid:
            mock_is_valid.return_value = True

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
        app.config["REDIRECT_FALA_REQUESTS"] = True

        with patch(
            "app.find_a_legal_adviser.routes.is_valid_category_code"
        ) as mock_is_valid:
            mock_is_valid.return_value = False

            with patch(
                "app.find_a_legal_adviser.routes.create_fala_url"
            ) as mock_create_fala_url:
                mock_create_fala_url.return_value = (
                    "https://staging.find-legal-advice.justice.gov.uk/check"
                )

                with patch(
                    "app.find_a_legal_adviser.routes.render_template"
                ) as mock_render_template:
                    client.get(
                        "/find-a-legal-adviser",
                        query_string={
                            "category": "invalid",
                            "secondary_category": "also-invalid",
                        },
                    )

                    mock_create_fala_url.assert_called_once_with(
                        category=None, secondary_category=None
                    )

                    mock_render_template.assert_called_once_with(
                        "categories/fala-interstitial.html",
                        fala_url="https://staging.find-legal-advice.justice.gov.uk/check",
                    )

    def test_redirect_with_mixed_valid_invalid_categories(self, app, client):
        """
        Test handling of mixed valid and invalid categories
        """
        app.config["REDIRECT_FALA_REQUESTS"] = True

        valid_category = "housing"
        invalid_category = "invalid"

        with patch(
            "app.find_a_legal_adviser.routes.is_valid_category_code"
        ) as mock_is_valid:

            def side_effect(arg):
                return arg == valid_category

            mock_is_valid.side_effect = side_effect

            with patch(
                "app.find_a_legal_adviser.routes.create_fala_url"
            ) as mock_create_fala_url:
                mock_create_fala_url.return_value = "https://staging.find-legal-advice.justice.gov.uk/check?categories=housing"

                with patch(
                    "app.find_a_legal_adviser.routes.render_template"
                ) as mock_render_template:
                    client.get(
                        "/find-a-legal-adviser",
                        query_string={
                            "category": valid_category,
                            "secondary_category": invalid_category,
                        },
                    )

                    mock_create_fala_url.assert_called_once_with(
                        category=valid_category, secondary_category=None
                    )

                    mock_render_template.assert_called_once_with(
                        "categories/fala-interstitial.html",
                        fala_url="https://staging.find-legal-advice.justice.gov.uk/check?categories=housing",
                    )

    def test_redirect_functions_not_called_when_flag_disabled(self, app, client):
        """
        Test that create_fala_url and render_template are not called
        when the feature flag is disabled
        """
        app.config["REDIRECT_FALA_REQUESTS"] = False

        response = client.get(
            "/find-a-legal-adviser",
            query_string={
                "category": "housing",
                "secondary_category": "eviction",
            },
        )

        assert response.status_code == 200

        with patch(
            "app.find_a_legal_adviser.routes.create_fala_url"
        ) as mock_create_fala_url:
            with patch(
                "app.find_a_legal_adviser.routes.render_template"
            ) as mock_render_template:
                mock_create_fala_url.assert_not_called()

                for call_args in mock_render_template.call_args_list:
                    assert call_args[0][0] != "categories/fala-interstitial.html"
