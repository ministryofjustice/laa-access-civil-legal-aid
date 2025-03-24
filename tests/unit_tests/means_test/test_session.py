from app.session import Eligibility


def test_has_partner():
    eligibility = Eligibility(
        forms={"about-you": {"has_partner": True, "in_dispute": False}},
        _notes={},
    )

    assert eligibility.has_partner

    eligibility = Eligibility(
        forms={"about-you": {"has_partner": True, "in_dispute": True}},
        _notes={},
    )

    assert not eligibility.has_partner


def test_employment_status():
    eligibility = Eligibility(
        forms={"about-you": {"is_employed": True, "is_self_employed": False}}, _notes={}
    )

    assert eligibility.is_employed

    assert not eligibility.is_self_employed

    assert eligibility.is_employed_or_self_employed


def test_partner_employment():
    eligibility = Eligibility(
        forms={
            "about-you": {
                "has_partner": True,
                "in_dispute": False,
                "partner_is_employed": True,
                "partner_is_self_employed": False,
            }
        },
        _notes={},
    )

    assert eligibility.is_partner_employed

    assert not eligibility.is_partner_self_employed

    eligibility = Eligibility(forms={"about-you": {"has_partner": False}}, _notes={})

    assert not eligibility.is_partner_employed

    assert not eligibility.is_partner_self_employed
