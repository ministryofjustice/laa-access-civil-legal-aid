from app.means_test.views import PropertyPayload


def test_property_payload_with_valid_data():
    form_data = {
        "submit": False,
        "is_main_home": "True",
        "other_shareholders": "0",
        "property_value": 230000,
        "mortgage_remaining": 100000,
        "mortgage_payments": 500,
        "is_rented": "1",
        "rent_amount": {
            "per_interval_value": 500,
            "per_interval_value_pounds": 50.0,
            "interval_period": "per_week",
        },
        "in_dispute": "False",
        "csrf_token": None,
    }
    expected_property_value = 23000000
    expected_mortgage_remaining = 10000000
    expected_rent = 500
    expected_share = 100

    payload = PropertyPayload(form_data)

    assert payload["value"] == expected_property_value
    assert payload["mortgage_left"] == expected_mortgage_remaining
    assert payload["share"] == expected_share
    assert payload["disputed"] == "False"
    assert payload["main"] == "True"

    rent = payload["rent"]["per_interval_value"]
    assert rent == expected_rent


def test_property_payload_with_missing_rent():
    form_data = form_data = {
        "submit": False,
        "is_main_home": "True",
        "other_shareholders": "0",
        "property_value": 230000,
        "mortgage_remaining": 100000,
        "mortgage_payments": 500,
        "is_rented": "1",
        "rent_amount": {
            "per_interval_value": None,
            "per_interval_value_pounds": None,
            "interval_period": None,
        },
        "in_dispute": "False",
        "csrf_token": None,
    }

    expected_property_value = 23000000
    expected_mortgage_remaining = 10000000
    expected_rent = {"per_interval_value": None, "interval_period": None}
    expected_share = 100

    payload = PropertyPayload(form_data)

    assert payload["value"] == expected_property_value
    assert payload["mortgage_left"] == expected_mortgage_remaining
    assert payload["share"] == expected_share
    assert payload["disputed"] == "False"
    assert payload["main"] == "True"

    rent = payload["rent"]
    assert rent == expected_rent
