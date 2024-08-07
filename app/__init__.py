from flask import Flask
from flask_assets import Bundle, Environment
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from govuk_frontend_wtf.main import WTFormsHelpers
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from .main.gtm import get_gtm_anon_id
import sentry_sdk

from app.config import Config

compress = Compress()
csrf = CSRFProtect()
limiter = Limiter(get_remote_address, default_limits=["2 per second", "60 per minute"])
talisman = Talisman()

if Config.SENTRY_DSN:
    sentry_sdk.init(
        dsn=Config.SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=0.01,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=0.2,
        # This can either be dev, uat, staging, or production.
        # It is set by CLA_ENVIRONMENT in the helm charts.
        environment=Config.ENVIRONMENT,
    )


def create_app(config_class=Config):
    app = Flask(__name__, static_url_path="/assets")
    assets = Environment(app)
    app.config.from_object(config_class)
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks = True
    app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("app"),
            PrefixLoader(
                {
                    "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja"),
                    "govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf"),
                }
            ),
        ]
    )

    # Set content security policy
    csp = {
        "default-src": "'self'",
        "script-src": [
            "'self'",
            "'sha256-GUQ5ad8JK5KmEWmROf3LZd9ge94daqNvd8xy9YS1iDw='",
            "*.googletagmanager.com",
        ],
        "connect-src": [
            "'self'",
            "*.google-analytics.com",
        ],
        "img-src": ["'self'", "*.googletagmanager.com"],
    }

    # Set permissions policy
    permissions_policy = {
        "accelerometer": "()",
        "autoplay": "()",
        "camera": "()",
        "cross-origin-isolated": "()",
        "display-capture": "()",
        "encrypted-media": "()",
        "fullscreen": "()",
        "geolocation": "()",
        "gyroscope": "()",
        "keyboard-map": "()",
        "magnetometer": "()",
        "microphone": "()",
        "midi": "()",
        "payment": "()",
        "picture-in-picture": "()",
        "publickey-credentials-get": "()",
        "screen-wake-lock": "()",
        "sync-xhr": "()",
        "usb": "()",
        "xr-spatial-tracking": "()",
        "clipboard-read": "()",
        "clipboard-write": "()",
        "gamepad": "()",
        "hid": "()",
        "idle-detection": "()",
        "unload": "()",
        "window-management": "()",
    }

    # Initialise app extensions
    assets.init_app(app)
    compress.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    talisman.init_app(
        app,
        content_security_policy=csp,
        permissions_policy=permissions_policy,
        content_security_policy_nonce_in=["script-src"],
        force_https=False,
        session_cookie_secure=False,
        session_cookie_http_only=True,
        session_cookie_samesite="Strict",
    )

    WTFormsHelpers(app)

    app.config["ASSETS_AUTO_BUILD"] = True  # Enable automatic rebuilding of assets
    app.config["ASSETS_MANIFEST"] = "cache"  # Enable cache manifest

    # Create static asset bundles
    css = Bundle(
        "src/scss/govuk-frontend.scss",
        filters="libsass, cssmin",  # Use SCSS filter to convert SCSS to CSS, then CSS minification
        output="dist/css/application-%(version)s.min.css",
    )
    # Concat all JS files into one.
    js = Bundle(
        "src/js/*.js",
        "*.js",
        filters="jsmin",
        output="dist/js/application-%(version)s.min.js",
    )
    # Concat all headscripts seperately so they can be loaded into the DOM head.
    headscripts = Bundle(
        "src/js/headscripts/*.js",
        filters="jsmin",
        output="dist/js/headscripts.min.js"
    )
    if "css" not in assets:
        assets.register("css", css)
    if "js" not in assets:
        assets.register("js", js)
    if "headscripts" not in assets:
        assets.register("headscripts", headscripts)

    # Register blueprints
    from app.main import bp as main_bp

    main_bp.context_processor(get_gtm_anon_id)

    app.register_blueprint(main_bp)

    return app
