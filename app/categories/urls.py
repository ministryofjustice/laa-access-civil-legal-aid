from flask import url_for, render_template, current_app
from app.categories import bp
from app.categories.views import CategoryPage
from app.categories.constants import (
    FAMILY,
    HOUSING,
    DOMESTIC_ABUSE,
    DISCRIMINATION,
    EDUCATION,
    COMMUNITY_CARE,
    BENEFITS,
    ASYLUM_AND_IMMIGRATION,
    MENTAL_CAPACITY,
    PUBLIC_LAW,
)


class IndexPage(CategoryPage):
    template = "categories/index.html"

    def dispatch_request(self):
        listing = [
            (FAMILY, url_for("categories.family.landing")),
            (HOUSING, url_for("categories.housing.landing")),
            (DOMESTIC_ABUSE, url_for("categories.domestic_abuse.landing")),
            (DISCRIMINATION, url_for("categories.discrimination.landing")),
            (EDUCATION, url_for("categories.send.landing")),
            (COMMUNITY_CARE, url_for("categories.community_care.landing")),
            (BENEFITS, url_for("categories.benefits.appeal")),
            (PUBLIC_LAW, url_for("categories.public.landing")),
            (ASYLUM_AND_IMMIGRATION, url_for("categories.asylum_immigration.landing")),
            (MENTAL_CAPACITY, url_for("categories.mental_capacity.landing")),
        ]
        return render_template(
            self.template,
            listing=listing,
            govukRebrand=current_app.config.get("GOVUK_REBRAND"),
        )


bp.add_url_rule(
    "/find-your-problem",
    view_func=IndexPage.as_view("index", template="categories/index.html"),
)
