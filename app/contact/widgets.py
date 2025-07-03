from govuk_frontend_wtf.wtforms_widgets import GovRadioInput
from app.means_test.widgets import MeansTestInputField


class ContactRadioInput(MeansTestInputField, GovRadioInput):
    def __init__(self, choice_hint, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        params = super().map_gov_params(field, **kwargs)
        self._assign_hint_text(params["items"])
        return params
