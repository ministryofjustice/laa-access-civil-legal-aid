from dataclasses import dataclass
from flask import redirect, current_app
import jwt
from enum import StrEnum


class CheckDestination(StrEnum):
    MEANS_TEST = "means-test"
    CONTACT = "contact"
    FALA = "fala"


class CheckCategory(StrEnum):
    DEBT = "debt"
    DISCRIMINATION = "discrimination"
    DOMESTIC_ABUSE = "domestic-abuse"
    CLINICAL_NEGLIGENCE = "clinneg"
    EDUCATION = "education"
    HOUSING = "housing"
    FAMILY = "family"
    IMMIGRATION_AND_ASYLUM = "immigration"
    WELFARE_BENEFITS = "benefits"
    NONE_OF_THE_ABOVE = "none"
    CONSUMER_ISSUES = "consumer"
    PERSONAL_INJURY = "pi"
    PUBLIC_LAW = "publiclaw"
    COMMUNITY_CARE = "commcare"
    MENTAL_HEALTH = "mentalhealth"
    CLAIMS_AGAINST_PUBLIC_AUTHORITIES = "aap"
    CRIME_CRIMINAL_LAW = "crime"
    EMPLOYMENT = "employment"


@dataclass
class CheckRedirect:
    """Handles redirecting the user to the correct page on Check if you can get legal aid.
    A signed post request is sent to the /receive-questions endpoint along with the users question answer map
    and a desired destination determined by the category routing logic.
    """

    check_endpoint = "/landing"
    destination: CheckDestination = None
    category = CheckCategory = None

    def __init__(self, destination, category):
        self.destination = destination
        self.category = category

    def submit_answers(self, question_answer_map):
        check_url = f"{current_app.config["CLA_PUBLIC_URL"]}{self.check_endpoint}"

        payload = {
            "answers": question_answer_map,
            "destination": self.destination,
            "category": self.category,
        }

        jwt_secret = current_app.config["CLA_PUBLIC_JWT_SECRET"]

        # Sign the payload
        token = jwt.encode(payload, jwt_secret, algorithm="HS256")

        return redirect(f"{check_url}?token={token}")
