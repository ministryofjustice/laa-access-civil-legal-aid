from govuk_frontend_wtf.wtforms_widgets import GovRadioInput, GovCheckboxesInput, GovTextInput
from flask_babel import lazy_gettext as _
from wtforms import SelectField


class BaseInputField:
    """Adds additional functionality to the GovUK Input widgets, allowing these to be set on a form by form basis,
    rather being required to be passed in to the widget when it is loaded via the template.
    """

    def __init__(
        self,
        show_divider: bool = False,
        is_inline: bool = False,
        hint_text: str = None,
        label_class: str = None,
        is_page_heading: bool = True,
        choice_hint: dict = None,
    ):
        super().__init__()
        self.show_divider = show_divider
        self.is_inline = is_inline
        self.hint_text = hint_text
        self.is_page_heading = is_page_heading  # This should be True for all single page questions
        self.label_class = label_class if label_class is not None else "govuk-fieldset__legend--l"
        self.choice_hint = choice_hint

    def _assign_hint_text(self, items):
        """
        Attach hint text to item value defined
        """
        for item in items:
            value = item.get("value")
            if value in self.choice_hint:
                item["hint"] = {"text": self.choice_hint[value]}

    def map_gov_params(self, field, **kwargs):
        if self.hint_text:
            kwargs["params"] = {"hint": {"text": self.hint_text}}

        params = super().map_gov_params(field, **kwargs)

        if self.is_inline:
            params["classes"] = "govuk-radios--inline"

        # Get or initialize the items list
        items = params.get("items", [])

        # Add divider if enabled and there are enough items
        if self.show_divider and len(items) >= 2:
            items[-2]["divider"] = _("or")

        # Adds hint text to choice
        if self.choice_hint:
            self._assign_hint_text(params["items"])

        # Handle pre-selected answer if present
        if field.data:
            for item in items:
                if item.get("value") == field.data:
                    item["checked"] = True

        if "fieldset" in params:
            params["fieldset"]["legend"]["classes"] = self.label_class
            params["fieldset"]["legend"]["isPageHeading"] = (
                self.is_page_heading
            )  # Sets the question text as the page H1
        else:
            params["label"]["classes"] = self.label_class

        return params


class MeansTestInputField(BaseInputField):
    """Adds additional functionality to the GovUK Input widgets, allowing these to be set on a form by form basis,
    rather being required to be passed in to the widget when it is loaded via the template.
    """

    def __init__(
        self,
        label_class: str = "govuk-fieldset__legend--s",
        is_page_heading: bool = False,
        is_inline: bool = True,
        *args,
        **kwargs,
    ):
        super().__init__(*args, label_class=label_class, is_page_heading=is_page_heading, is_inline=is_inline, **kwargs)


class RenderConditionalFields:
    def map_gov_params(self, field, **kwargs):
        params = super().map_gov_params(field, **kwargs)

        if "conditional" in kwargs:
            conditional = kwargs.pop("conditional")
            for item in params["items"]:
                if item["value"] == conditional["value"]:
                    item["conditional"] = {"html": conditional["html"]}
        return params


class BaseRadioInput(BaseInputField, GovRadioInput):
    pass


class BaseCheckboxInput(BaseInputField, GovCheckboxesInput):
    def __init__(self, *args, behaviour=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.behaviour = behaviour

    def map_gov_params(self, field, **kwargs):
        params = super().map_gov_params(field, **kwargs)
        if self.behaviour:
            params["items"][-1]["behaviour"] = self.behaviour
        return params


class BaseTextInput(BaseInputField, GovTextInput):
    pass


class MeansTestRadioInput(MeansTestInputField, RenderConditionalFields, GovRadioInput):
    pass


class MeansTestCheckboxInput(MeansTestInputField, RenderConditionalFields, GovCheckboxesInput):
    pass


class MoneyInput(GovTextInput):
    def __init__(self, label_class: str = "govuk-fieldset__legend--s"):
        self.label_class = label_class

    def map_gov_params(self, field, **kwargs):
        kwargs["params"] = {
            "prefix": {"text": " £"},
            "label": {"classes": self.label_class},
            "inputmode": "numeric",
            "classes": "govuk-input--width-10",
        }
        params = super().map_gov_params(field, **kwargs)
        return params


class ContactSelectField(SelectField):
    def pre_validate(self, form):
        """Override to prevent WTForms' internal choice validation"""
        pass
