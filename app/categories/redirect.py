from dataclasses import dataclass
import requests
from flask import redirect, abort
import jwt
from enum import StrEnum
from app.config import Config


class CheckDestination(StrEnum):
    MEANS_TEST = "means-test"
    CONTACT = "contact"
    FALA = "fala"


@dataclass
class CheckRedirect:
    """Handles redirecting the user to the correct page on Check if you can get legal aid.
    A signed post request is sent to the /receive-questions endpoint along with the users question answer map
    and a desired destination determined by the category routing logic.
    """

    check_url = f"{Config.CLA_PUBLIC_URL}/receive-answers"
    destination: CheckDestination

    def submit_answers(self, question_answer_map):
        payload = {"answers": question_answer_map, "redirect": self.destination}

        # Sign the payload
        token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                self.check_url, json={"token": token}, headers=headers
            )

            if response.status_code != 200:
                abort(500)
            json_response = response.json()
            if "redirect_url" not in json_response:
                abort(500)
            return redirect(json_response["redirect_url"])

        except requests.exceptions.RequestException:
            abort(500)
