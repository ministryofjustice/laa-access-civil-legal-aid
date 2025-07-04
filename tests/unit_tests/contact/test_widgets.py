from app.contact.widgets import ContactRadioInput, GovRadioInput
from unittest.mock import patch, Mock


def test_assign_hint_text_adds_hints_correctly():
    choice_hint = {"call": "You will call us", "callback": "We will call you"}

    items = [
        {"value": "call", "text": "I will call"},
        {"value": "callback", "text": "Call me back"},
        {"value": "thirdparty", "text": "Someone else calls"},
    ]

    widget = ContactRadioInput(choice_hint=choice_hint)

    widget._assign_hint_text(items)

    assert items[0]["hint"] == {"text": "You will call us"}
    assert items[1]["hint"] == {"text": "We will call you"}
    assert "hint" not in items[2]


def test_map_gov_params_calls_assign_hint_text():
    choice_hint = {"call": "I will call", "callback": "Call me back"}
    radio_input = ContactRadioInput(choice_hint=choice_hint)
    mock_items = [{"value": "call"}, {"value": "callback"}]

    mocked_parent_response = {"items": mock_items, "label": {"classes": ""}, "fieldset": {"legend": {"classes": ""}}}

    with (
        patch.object(GovRadioInput, "map_gov_params", return_value=mocked_parent_response) as mock_super_map,
        patch.object(radio_input, "_assign_hint_text") as mock_assign,
    ):
        radio_input.map_gov_params(Mock())

        mock_super_map.assert_called_once()
        mock_assign.assert_called_once_with(mock_items)
