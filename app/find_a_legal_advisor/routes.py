from app.find_a_legal_advisor import bp
from flask import render_template, request
from app.find_a_legal_advisor.forms import FindLegalAdviserForm
from app.find_a_legal_advisor.laalaa import laalaa_search, is_valid_category_code
from app.find_a_legal_advisor.utils import get_pagination_data


@bp.get("/find-a-legal-advisor")
def search():
    form = FindLegalAdviserForm(request.args)

    category: str | None = request.args.get("category", default=None, type=str)
    secondary_category: str | None = request.args.get(
        "secondary_category", default=None, type=str
    )
    if not is_valid_category_code(category):
        category = None

    if "postcode" in request.args and form.validate():
        postcode: str | None = form.postcode.data
        page_num: int = request.args.get("page", 1, type=int)
        postcode_region: str = form.postcode_region
        return result_page(
            postcode, category, secondary_category, page_num, postcode_region
        )

    return render_template(
        "find_a_legal_adviser/search.html",
        form=form,
        category=category,
        secondary_category=secondary_category,
    )

    postcode: str,
    category: str = None,
    secondary_category: str = None,
    page_num: int = 1,
    postcode_region: str = None,
):
    results = laalaa_search(
        postcode=postcode, categories=[category, secondary_category], page=page_num
    )

    pagination_data = get_pagination_data(
        results, postcode=postcode, category=category, current_page_num=page_num
    )

    return render_template(
        "find_a_legal_adviser/results.html",
        data=results,
        category=category,
        secondary_category=secondary_category,
        pagination_data=pagination_data,
        postcode_region=postcode_region,
    )
