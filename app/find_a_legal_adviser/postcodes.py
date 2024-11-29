from .laalaa import kwargs_to_urlparams
from flask import current_app
import requests


def postcodes_io_url(endpoint: str = "postcodes", **kwargs):
    api_host = current_app.config["POSTCODES_IO_URL"]
    params = kwargs_to_urlparams(**kwargs)
    return f"{api_host}/{endpoint}/?{params}"


def postcode_lookup(postcode: str):
    response = requests.get(postcodes_io_url(q=postcode, limit=1))
    postcode_info = response.json()["result"]
    if len(postcode_info) > 0:
        return postcode_info[0]
    return None


def get_postcode_region(postcode: str) -> str:
    postcode_info = postcode_lookup(postcode)
    if postcode_info is None:
        return "Unknown"

    if "country" not in postcode_info:
        return "Unknown"

    region: str = postcode_info["country"]

    if "channel islands" in postcode_info["country"].lower():
        if "jersey" in postcode_info["nhs_ha"].lower():
            region = "Jersey"
        if "guernsey" in postcode_info["nhs_ha"].lower():
            region = "Guernsey"

    return region.strip()
