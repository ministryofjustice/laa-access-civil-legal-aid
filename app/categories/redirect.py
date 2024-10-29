from dataclasses import dataclass
from flask import redirect
import jwt
from enum import StrEnum
from app.config import Config


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

    check_url = f"{Config.CLA_PUBLIC_URL}/user-receive-answers"
    destination: CheckDestination = None
    category = CheckCategory = None

    def __init__(self, destination, category):
        self.destination = destination
        self.category = category

    def submit_answers(self, question_answer_map):
        payload = {
            "answers": question_answer_map,
            "destination": self.destination,
            "category": self.category,
        }

        # Sign the payload
        token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

        return redirect(f"{self.check_url}?token={token}")
