from govuk_frontend_wtf.wtforms_widgets import GovRadioInput


class CategoryRadioInput(GovRadioInput):
    """Override of the base GovUK Frontend Radio Input to support setting a CSS class on the label text."""

    def __init__(self, show_divider: bool = False, is_inline: bool = False):
        super().__init__()
        self.show_divider = show_divider
        self.is_inline = is_inline

    def map_gov_params(self, field, **kwargs):
        label_class = "govuk-fieldset__legend--l"

        params = super().map_gov_params(field, **kwargs)
        if self.is_inline:
            params["classes"] = "govuk-radios--inline"

        # Get or initialize the items list
        items = params.get("items", [])

        # Add divider if enabled and there are enough items
        if self.show_divider and len(items) >= 2:
            items[-2]["divider"] = "or"

        # Handle pre-selected answer if present
        if field.data:
            for item in items:
                if item.get("value") == field.data:
                    item["checked"] = True

        # Get or initialize the items list
        items = params.get("items", [])

        # Add divider if enabled and there are enough items
        if self.show_divider and len(items) >= 2:
            items[-2]["divider"] = "or"

        # Handle pre-selected answer if present
        if field.data:
            for item in items:
                if item.get("value") == field.data:
                    item["checked"] = True

        params["fieldset"]["legend"]["classes"] = label_class
        return params
