from govuk_frontend_wtf.wtforms_widgets import GovRadioInput


class CategoryRadioInput(GovRadioInput):
    """Override of the base GovUK Frontend Radio Input to support setting a CSS class on the label text."""

    def map_gov_params(self, field, **kwargs):
        label_class = "govuk-fieldset__legend--l"

        params = super().map_gov_params(field, **kwargs)

        params["fieldset"]["legend"]["classes"] = label_class
        return params
