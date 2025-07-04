import pytest
from unittest.mock import patch, Mock
from app.main.widgets import (
    BaseRadioInput,
    BaseCheckboxInput,
    BaseTextInput,
    ContactSelectField,
)
from wtforms import Form


def test_assign_hint_text_adds_hints_correctly():
    choice_hint = {"call": "You will call us", "callback": "We will call you"}

    items = [
        {"value": "call", "text": "I will call"},
        {"value": "callback", "text": "Call me back"},
        {"value": "thirdparty", "text": "Someone else calls"},
    ]

    widget = BaseRadioInput(choice_hint=choice_hint)

    widget._assign_hint_text(items)

    assert items[0]["hint"] == {"text": "You will call us"}
    assert items[1]["hint"] == {"text": "We will call you"}
    assert "hint" not in items[2]


def test_base_radio_map_gov_params_applies_all_customisations():
    widget = BaseRadioInput(
        hint_text="Some hint",
        is_inline=True,
        choice_hint={"a": "Hint for A"},
        show_divider=True,
    )

    mock_field = Mock()
    mock_field.data = "a"

    parent_response = {
        "items": [{"value": "a"}, {"value": "b"}],
        "fieldset": {"legend": {"classes": ""}},
        "label": {"classes": ""},
    }

    with patch("govuk_frontend_wtf.wtforms_widgets.GovRadioInput.map_gov_params", return_value=parent_response):
        result = widget.map_gov_params(mock_field)

    assert result["items"][0]["checked"] is True
    assert result["items"][0]["hint"]["text"] == "Hint for A"
    assert result["items"][0]["divider"] == "or"
    assert "divider" not in result["items"][1]
    assert result["classes"] == "govuk-radios--inline"
    assert result["fieldset"]["legend"]["classes"] == "govuk-fieldset__legend--l"
    assert result["fieldset"]["legend"]["isPageHeading"] is True


def test_checkbox_widget_applies_behaviour():
    widget = BaseCheckboxInput(behaviour="exclusive")

    mock_field = Mock()
    mock_field.data = "test"

    parent_response = {
        "items": [{"value": "one"}, {"value": "test"}],
        "label": {"classes": ""},
        "fieldset": {"legend": {"classes": ""}},
    }

    with patch("govuk_frontend_wtf.wtforms_widgets.GovCheckboxesInput.map_gov_params", return_value=parent_response):
        result = widget.map_gov_params(mock_field)

    assert result["items"][-1]["behaviour"] == "exclusive"


def test_text_input_widget_maps_label_class():
    widget = BaseTextInput(label_class="govuk-label--xl")

    mock_field = Mock()
    mock_field.data = ""

    parent_response = {
        "label": {"classes": ""},
        "fieldset": {"legend": {"classes": ""}},
    }

    with patch("govuk_frontend_wtf.wtforms_widgets.GovTextInput.map_gov_params", return_value=parent_response):
        result = widget.map_gov_params(mock_field)

    assert result["fieldset"]["legend"]["classes"] == "govuk-label--xl"


def test_contact_select_field_skips_validation():
    class DummyForm(Form):
        contact_method = ContactSelectField(label="Choose", choices=[("1", "One")])

    form = DummyForm()
    field = form.contact_method

    try:
        field.pre_validate(form)
    except Exception:
        pytest.fail("pre_validate() should not raise an exception")
