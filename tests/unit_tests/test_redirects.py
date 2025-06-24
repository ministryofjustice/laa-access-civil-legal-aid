import pytest
from flask import url_for


@pytest.mark.parametrize(
    "path, expected_endpoint",
    [
        ("/scope/diagnosis", "categories.index"),
        ("/contact", "contact.contact_us"),
        (
            "/scope/refer/discrimination",
            "categories.discrimination.cannot_find_your_problem",
        ),
    ],
)
def test_redirect_map(client, path, expected_endpoint):
    """Tests static redirects defined in REDIRECT_MAP."""
    response = client.get(path, follow_redirects=False)
    assert response.status_code == 301

    expected_url = url_for(expected_endpoint, _external=False)
    assert response.headers["Location"].endswith(expected_url)


@pytest.mark.parametrize(
    "category, expected_category, expected_secondary",
    [
        ("clinneg", "med", None),
        ("commcare", "com", None),
        ("traffickingandslavery", "immas", None),
        ("mentalhealth", "mhe", "com"),
        ("unknown", None, None),
    ],
)
def test_fala_redirect(client, category, expected_category, expected_secondary):
    """Tests FALA category redirects."""
    response = client.get(f"/scope/refer/legal-adviser?category={category}", follow_redirects=False)
    assert response.status_code == 301

    if expected_category:
        expected_url = url_for(
            "find-a-legal-adviser.search",
            category=expected_category,
            secondary_category=expected_secondary,
            _external=False,
        ).rstrip("&")
    else:
        expected_url = url_for("find-a-legal-adviser.search", _external=False)

    assert response.headers["Location"] == expected_url


def test_scope_diagnosis_redirect(client):
    """Tests that any /scope/diagnosis/* path redirects to main.session_expired."""
    response = client.get("/scope/diagnosis/n223", follow_redirects=False)
    assert response.status_code == 301

    expected_url = url_for("main.session_expired", _external=False)
    assert response.headers["Location"] == expected_url


def test_404_for_unknown_path(client):
    """Tests that an unknown path returns 404."""
    response = client.get("/unknown/path", follow_redirects=False)
    assert response.status_code == 404
