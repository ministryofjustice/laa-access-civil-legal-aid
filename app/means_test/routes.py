from app.means_test import bp


@bp.get("/mean-test-review")
def review():
    return "I am a holding page"
