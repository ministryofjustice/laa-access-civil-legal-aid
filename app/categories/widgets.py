from govuk_frontend_wtf.wtforms_widgets import GovRadioInput, GovCheckboxesInput
from flask_babel import lazy_gettext as _


class CategoryInputField:
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
    ):
        super().__init__()
        self.show_divider = show_divider
        self.is_inline = is_inline
        self.hint_text = hint_text
        self.is_page_heading = is_page_heading  # This should be True for all single page questions
        self.label_class = label_class if label_class is not None else "govuk-fieldset__legend--l"

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

        # Handle pre-selected answer if present
        if field.data:
            for item in items:
                if item.get("value") == field.data:
                    item["checked"] = True

        params["fieldset"]["legend"]["classes"] = self.label_class
        params["fieldset"]["legend"]["isPageHeading"] = self.is_page_heading  # Sets the question text as the page H1
        return params


class CategoryRadioInput(CategoryInputField, GovRadioInput):
    pass


class CategoryCheckboxInput(CategoryInputField, GovCheckboxesInput):
    def __init__(self, *args, behaviour=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.behaviour = behaviour

    def map_gov_params(self, field, **kwargs):
        params = super().map_gov_params(field, **kwargs)
        if self.behaviour:
            params["items"][-1]["behaviour"] = self.behaviour
        return params
