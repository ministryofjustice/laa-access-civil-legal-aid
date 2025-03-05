from app.session import Eligibility


def test_is_yes():
    eligibility = Eligibility(forms={"form1": {"field1": "1"}})

    assert eligibility.is_yes("form1", "field1")

    assert not eligibility.is_yes("form1", "field2")

    assert not eligibility.is_yes("form2", "field1")


def test_is_no():
    eligibility = Eligibility(forms={"form1": {"field1": "0"}})

    assert eligibility.is_no("form1", "field1")

    assert not eligibility.is_no("form1", "field2")

    assert not eligibility.is_no("form2", "field1")


def test_has_partner():
    eligibility = Eligibility(
        forms={"about-you": {"has_partner": True, "are_you_in_a_dispute": False}}
    )

    assert eligibility.has_partner

    eligibility = Eligibility(
        forms={"about-you": {"has_partner": True, "are_you_in_a_dispute": True}}
    )

    assert not eligibility.has_partner


def test_employment_status():
    eligibility = Eligibility(
        forms={"about-you": {"is_employed": True, "is_self_employed": False}}
    )

    assert eligibility.is_employed

    assert not eligibility.is_self_employed

    assert eligibility.is_employed_or_self_employed


def test_partner_employment():
    eligibility = Eligibility(
        forms={
            "about-you": {
                "has_partner": True,
                "are_you_in_a_dispute": False,
                "partner_is_employed": True,
                "partner_is_self_employed": False,
            }
        }
    )

    assert eligibility.is_partner_employed

    assert not eligibility.is_partner_self_employed

    eligibility = Eligibility(forms={"about-you": {"has_partner": False}})

    assert not eligibility.is_partner_employed

    assert not eligibility.is_partner_self_employed
