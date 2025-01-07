from flask import current_app


def backend_url(endpoint: str):
    backend_host_url = current_app.config["CLA_BACKEND_URL"]
    api_route = "/checker/api/v1/"
    endpoint = endpoint
    return f"{backend_host_url}{api_route}{endpoint}"
