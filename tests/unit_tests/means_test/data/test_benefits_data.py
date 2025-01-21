from app.means_test.data import BenefitsData, MoneyInterval


def test_benefits_data_passported_benefits():
    benefits_data = BenefitsData(**{"benefits": ["universal_credit", "income_support"]})
    expected_payload = {
        "specific_benefits": {
            "pension_credit": False,
            "job_seekers_allowance": False,
            "employment_support": False,
            "universal_credit": True,
            "income_support": True,
        },
        "on_passported_benefits": True,
        "child_benefits": MoneyInterval(0).to_json(),
    }
    actual_payload = benefits_data.to_payload()
    assert actual_payload == expected_payload


def test_benefits_data_passported_benefits_with_child_benefits():
    """When on passported benefits then child_benefits payload is always 0"""
    child_benefits = MoneyInterval(["200", "per_week"])
    benefits_data = BenefitsData(
        **{
            "benefits": ["universal_credit", "income_support"],
            "child_benefits": child_benefits,
        }
    )
    expected_payload = {
        "specific_benefits": {
            "pension_credit": False,
            "job_seekers_allowance": False,
            "employment_support": False,
            "universal_credit": True,
            "income_support": True,
        },
        "on_passported_benefits": True,
        "child_benefits": MoneyInterval(0).to_json(),
    }
    actual_payload = benefits_data.to_payload()
    assert actual_payload == expected_payload


def test_benefits_data_no_benefits():
    benefits_data = BenefitsData(**{"benefits": []})
    expected_payload = {
        "specific_benefits": {
            "pension_credit": False,
            "job_seekers_allowance": False,
            "employment_support": False,
            "universal_credit": False,
            "income_support": False,
        },
        "on_passported_benefits": False,
        "child_benefits": MoneyInterval(0).to_json(),
    }
    actual_payload = benefits_data.to_payload()
    assert actual_payload == expected_payload


def test_benefits_data_child_benefits():
    child_benefits = MoneyInterval(["200", "per_week"])
    benefits_data = BenefitsData(
        **{"benefits": ["child_benefit"], "child_benefits": child_benefits}
    )
    expected_payload = {
        "specific_benefits": {
            "pension_credit": False,
            "job_seekers_allowance": False,
            "employment_support": False,
            "universal_credit": False,
            "income_support": False,
        },
        "on_passported_benefits": False,
        "child_benefits": {
            "per_interval_value": 20000,
            "interval_period": "per_week",
        },
    }
    actual_payload = benefits_data.to_payload()
    assert actual_payload == expected_payload
