from flask import Blueprint

bp = Blueprint(
    "mental_capacity",
    __name__,
    template_folder="./templates",
)

from app.categories.mental_capacity import urls  # noqa: E402,F401
