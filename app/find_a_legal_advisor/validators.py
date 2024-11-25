from wtforms.validators import ValidationError
from app.find_a_legal_advisor.postcode_lookup import get_postcode_region
from requests.exceptions import ConnectionError


class ValidRegionPostcode:
    def __init__(self):
        self.region_messages = {
            "Scotland": "This service is not available in Scotland",
            "Northern Ireland": "This service is not available in Northern Ireland",
            "Jersey": "No results returned for Jersey, try a postcode in England or Wales",
            "Guernsey": "No results returned for Guernsey, try a postcode in England or Wales",
            "Isle of Man": "No results returned for the Isle of Man, try a postcode in England or Wales",
        }
        self.default_message = "This service is only available in England and Wales"
        self.valid_regions = {"England", "Wales", "Scotland", "Northern Ireland"}

    def __call__(self, form, field):
        if not field.data:
            # Let the InputRequired validator handle this
            return

        try:
            region = get_postcode_region(field.data)
            form.postcode_region = region  # Store the region information on the form so we don't need to look it up again

            # Handle case sensitivity
            if isinstance(region, str):
                region = region.strip()

                # Check against valid regions (case-insensitive)
                if not any(
                    region.lower() == valid.lower() for valid in self.valid_regions
                ):
                    message = self.region_messages.get(region, self.default_message)
                    raise ValidationError(message)
            else:
                raise ValidationError("Postcode not found")

        except ValidationError:
            # Re-raise validation errors
            raise
        except ConnectionError:
            raise ValidationError(
                "This service is not available at the moment, try again later"
            )
        except Exception:
            raise ValidationError("Postcode not found")
