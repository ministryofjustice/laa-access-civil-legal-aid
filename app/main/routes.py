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
    Response,
    session,
)
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import HTTPException
from app.main import bp
from app.main.gtm import get_gtm_anon_id_from_cookie
from app.main.forms import CookiesForm


@bp.get("/")
def start_page():
    """Directs the user to the start page of the service, hosted on GOV.UK
    This is the endpoint directed to from the header text, clicking this link will reset the users' session.
    """
    session.clear()
    if current_app.config.get("ENVIRONMENT") != "production":
        return redirect(url_for("categories.index"))

    from app.main import get_locale

    GOVUK_url = (
        current_app.config.get("WELSH_GOV_UK_START_PAGE")
        if get_locale() == "cy"
        else current_app.config.get("GOV_UK_START_PAGE")
    )
    return redirect(GOVUK_url)


@bp.get("/start")
def start():
    """This is the main entry point for the service from www.gov.uk/check-legal-aid
    The Welsh version of this page directs the user to /start?locale=cy_GB, we need to set their locale cookie accordingly
    """
    session.clear()

    response = redirect(url_for("categories.index"))
    locale = request.args.get("locale")
    if locale:
        response = set_locale_cookie(response, locale)
    return response


@bp.get("/start-bsl")
def start_bsl():
    """This an entry point for the service from www.gov.uk/check-legal-aid
    This is a route for users who need to contact us via BSL, they are routed directly to the contact us page
    """
    session.clear()

    response = redirect(url_for("contact.contact_us"))
    locale = request.args.get("locale")
    if locale:
        response = set_locale_cookie(response, locale)
    return response


def set_locale_cookie(response: Response, locale: str) -> Response:
    """Takes in a response and a locale string, sets the locale cookie on the response and returns it"""
    if not locale or not isinstance(locale, str):
        return response
    locale = locale.strip("_GB")
    if locale not in current_app.config["LANGUAGES"]:
        return abort(404)

    expires = datetime.datetime.now() + datetime.timedelta(days=30)
    response.set_cookie(
        "locale", locale, expires=expires, secure=True, httponly=True, samesite="Strict"
    )
    return response


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
    response = set_locale_cookie(response, locale)
    return response


@bp.route("/status", methods=["GET"])
def status():
    return "OK"


@bp.route("/service-unavailable", methods=["GET"])
def service_unavailable_page():
    if not current_app.config["SERVICE_UNAVAILABLE"]:
        return redirect(url_for("categories.index"))
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
        response = make_response(
            render_template(
                "cookies.html",
                form=form,
            )
        )

        if cookies_policy["analytics"].lower() == "no":
            for name, value in request.cookies.items():
                if name.startswith("_ga") or name.startswith("gtm_anon_id"):
                    response.delete_cookie(name)

        # Set cookies policy for one year
        response.set_cookie(
            "cookies_policy",
            json.dumps(cookies_policy),
            max_age=31557600,
            secure=True,
            httponly=False,  # This needs to be read by the client so we set HTTPOnly to false.
            samesite="Strict",
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
    return render_template("cookies.html")


@bp.route("/privacy", methods=["GET"])
def privacy():
    return render_template("main/privacy.html")


@bp.route("/online-safety")
def online_safety():
    return render_template("main/online-safety.html")


@bp.route("/session-expired", methods=["GET"])
def session_expired():
    session.clear()
    session["gtm_anon_id"] = get_gtm_anon_id_from_cookie()
    return render_template("session_expired.html")


@bp.app_errorhandler(HTTPException)
def http_exception(error):
    return render_template(f"{error.code}.html"), error.code


@bp.app_errorhandler(CSRFError)
def csrf_error(error):
    flash("The form you were submitting has expired. Please try again.")
    return redirect(request.full_path)


@bp.before_app_request
def service_unavailable_middleware():
    if not current_app.config["SERVICE_UNAVAILABLE"]:
        return

    # Allow requests for static assets, this is required for the service unavailable page to render correctly
    if request.path.startswith("/assets/"):
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
