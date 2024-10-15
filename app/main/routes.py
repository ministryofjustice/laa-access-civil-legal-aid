import datetime
from urllib.parse import urlparse
from flask import (
    flash,
    json,
    make_response,
    redirect,
    render_template,
    request,
    current_app,
    url_for,
    abort,
)
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import HTTPException

from app.main import bp
from app.main.forms import CookiesForm


@bp.route("/main")
def index():
    return redirect(url_for("categories.index"))


@bp.route("/locale/<locale>")
def set_locale(locale):
    """
    Set locale cookie
    """
    if locale not in current_app.config["LANGUAGES"]:
        abort(404)

    if request.referrer:
        parse = urlparse(request.referrer)
        redirect_url = ["/", parse.path.strip("/")]
        if parse.query:
            redirect_url.append("?" + parse.query)
    else:
        redirect_url = ["/"]

    response = redirect("".join(redirect_url))
    expires = datetime.datetime.now() + datetime.timedelta(days=30)
    response.set_cookie(
        "locale", locale, expires=expires, secure=(not current_app.debug), httponly=True
    )
    return response


@bp.route("/status", methods=["GET"])
def status():
    return "OK"


@bp.route("/service-unavailable", methods=["GET"])
def service_unavailable_page():
    if not current_app.config["SERVICE_UNAVAILABLE"]:
        return redirect(url_for("main.index"))
    abort(503)


@bp.route("/accessibility", methods=["GET"])
def accessibility():
    return render_template("accessibility.html")


@bp.route("/cookies", methods=["GET", "POST"])
def cookies():
    form = CookiesForm()
    # Default cookies policy to reject all categories of cookie
    cookies_policy = {"functional": "no", "analytics": "no"}

    if form.validate_on_submit():
        # Update cookies policy consent from form data
        cookies_policy["functional"] = form.functional.data
        cookies_policy["analytics"] = form.analytics.data

        # Create flash message confirmation before rendering template
        flash("You’ve set your cookie preferences.", "success")

        # Create the response so we can set the cookie before returning
        response = make_response(render_template("cookies.html", form=form))

        # Set cookies policy for one year
        response.set_cookie(
            "cookies_policy", json.dumps(cookies_policy), max_age=31557600
        )
        return response
    elif request.method == "GET":
        if request.cookies.get("cookies_policy"):
            # Set cookie consent radios to current consent
            cookies_policy = json.loads(request.cookies.get("cookies_policy"))
            form.functional.data = cookies_policy["functional"]
            form.analytics.data = cookies_policy["analytics"]
        else:
            # If conset not previously set, use default "no" policy
            form.functional.data = cookies_policy["functional"]
            form.analytics.data = cookies_policy["analytics"]
    return render_template("cookies.html", form=form)


@bp.route("/privacy", methods=["GET"])
def privacy():
    return render_template("privacy.html")


@bp.app_errorhandler(HTTPException)
def http_exception(error):
    return render_template(f"{error.code}.html"), error.code


@bp.app_errorhandler(CSRFError)
def csrf_error(error):
    flash("The form you were submitting has expired. Please try again.")
    return redirect(request.full_path)


@bp.before_request
def service_unavailable_middleware():
    if not current_app.config["SERVICE_UNAVAILABLE"]:
        return

    service_unavailable_url = url_for("main.service_unavailable_page")
    exempt_urls = [
        service_unavailable_url,
        url_for("main.status"),
        url_for("main.cookies"),
        url_for("main.accessibility"),
        url_for("main.privacy"),
        url_for("main.set_locale", locale="en"),
        url_for("main.set_locale", locale="cy"),
    ]
    if request.path not in exempt_urls:
        return redirect(service_unavailable_url)
