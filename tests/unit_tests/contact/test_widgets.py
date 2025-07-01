from app.contact.widgets import ContactRadioInput


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
