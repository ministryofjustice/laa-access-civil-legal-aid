import math
from flask import url_for

items_per_page = 10
max_pages = 9


def get_pagination_data(
    results_data: dict,
    current_page_num: int = 1,
    postcode: str | None = None,
    category: str | None = None,
    secondary_category: str | None = None,
) -> dict:
    pagination_data = {}

    num_pages = min(math.ceil(results_data["count"] / items_per_page), max_pages)

    pagination_items = []
    for page_num in range(1, num_pages + 1):
        item = {
            "number": page_num,
            "href": url_for(
                "find-a-legal-advisor.search",
                postcode=postcode,
                category=category,
                secondary_category=secondary_category,
                page=page_num,
            ),
        }
        if page_num == current_page_num:
            item["current"] = True
        pagination_items.append(item)

    if current_page_num > 1:
        pagination_data["previous"] = {
            "href": url_for(
                "find-a-legal-advisor.search",
                postcode=postcode,
                category=category,
                secondary_category=secondary_category,
                page=current_page_num - 1,
            )
        }

    if current_page_num < num_pages:
        pagination_data["next"] = {
            "href": url_for(
                "find-a-legal-advisor.search",
                postcode=postcode,
                category=category,
                secondary_category=secondary_category,
                page=current_page_num + 1,
            )
        }

    pagination_data["items"] = pagination_items

    return pagination_data
