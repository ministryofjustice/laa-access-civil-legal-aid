# MOJ GOV.UK Frontend Flask

This is a clone from the HM Land Registery Flask skeleton [GOV.UK Frontend Flask](https://github.com/LandRegistry/govuk-frontend-flask). Thank you, Land Registry.

![govuk-frontend 5.1.0](https://img.shields.io/badge/govuk--frontend%20version-5.1.0-005EA5?logo=gov.uk&style=flat)

**GOV.UK Frontend Flask is a [community tool](https://design-system.service.gov.uk/community/resources-and-tools/) of the [GOV.UK Design System](https://design-system.service.gov.uk/). The Design System team is not responsible for it and cannot support you with using it. Contact the [maintainers](#contributors) directly if you need [help](#support) or you want to request a feature.**

This is a template [Flask](https://flask.palletsprojects.com) app using the [GOV.UK Frontend](https://frontend.design-system.service.gov.uk/) and [GOV.UK Design System](https://design-system.service.gov.uk/) which is designed to get a new project started quicker. It is also a reference implementation of two core packages:

- [GOV.UK Frontend Jinja](https://github.com/LandRegistry/govuk-frontend-jinja) which provides Jinja macros of GOV.UK components
- [GOV.UK Frontend WTForms](https://github.com/LandRegistry/govuk-frontend-wtf) which provides WTForms widgets to integrate the above Jinja macros into form generation and validation

The app is provided intentionally bare, with just the essential parts that all services need, such as error pages, accessibility statement, cookie banner, cookie page and privacy notice. It uses a number of other packages to provide the [features](#features) described below with sensible and best-practice defaults. Please read the [next steps](#next-steps) section for guidance on how to start building out your app on top of this template.

# Getting started

## Local install for development:

### Setup

Create a virtual environment and install the python dependencies:

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.in -r requirements_dev.in
```

Note on dependencies:

* requirements.in are the direct dependencies of the app.
* requirements_dev.in are the dependencies needed only during development - linters, code formatting etc
* (requirements*.txt - in a production system we'd generate a .txt from each .in file. The .txt file includes all direct
dependencies in the .in, plus their dependencies too (indirect dependencies). And all dependencies have their exact 
version specified ('pinned'). This ensures production environment installs exactly the same as the test environment and
what developers install.)

### Assets setup

For this you'll need to install node. 

`npm install`

Once installed you now have access to GOVUK components, stylesheets and JS via the `node_module`

To copy some of the assets you'll need into your project, run the following:

`npm run build`

Ensure you do this before starting your Flask project as you're JS and SCSS imports will fail in the flask run.

### Demo assets

For the demo of the MOJ Flask Skeleton, you'll need the `govuk_components` yaml files.

```shell
./build.sh
```

You will not need this in your development project. This is only for the MOJ Flask Skeleton Demo.

### Configuration environment variables

Create your local config file `.env` from the template file:

```shell
cp .env.example .env
```

Don't worry, you can't commit your `.env` file.

### Run the service

```shell
source .venv/bin/activate
flask --app app run --debug --port=8000
```

Now you can browse: http://127.0.0.1:8000

(The default port for flask apps is 5000, but on Macs this is often found to conflict with Apple's Airplay service, hence using another port here.)

## Running in Docker

For local development and deployments.

### Set local Docker environment variables

In the `compose.yml` file you will find a number of environment variables. These are injected as global variables into the app and pre-populated into page templates as appropriate. Enter your specific service information for the following:

- CONTACT_EMAIL
- CONTACT_PHONE
- DEPARTMENT_NAME
- DEPARTMENT_URL
- SERVICE_NAME
- SERVICE_PHASE
- SERVICE_URL

You must also set a new unique `SECRET_KEY`, which is used to securely sign the session cookie and CSRF tokens. It should be a long random `bytes` or `str`. You can use the output of this Python comand to generate a new key:

```shell
python -c 'import secrets; print(secrets.token_hex())'
```

### Run containers

```shell
docker compose up --build
```

## Demos

There are some helpful demos included by default that show all of the components available from GOV.UK Frontend Jinja and a selection of forms and validation patterns from GOV.UK Frontend WTForms. These are located in the `app/demos` and `app/templates/demos` directories, along with the `demos` blueprint. Use them for reference whilst building your service, but make sure to delete them, along with the relevant section in `build.sh`, before deploying the app.

## Testing

To run the tests:

```shell
python -m pytest --cov=app --cov-report=term-missing --cov-branch
```

## Playwright Testing

To run tests:

```shell
pytest
```

Run tests in headed mode:

```shell
pytest --headed
```

Run tests in a different browser (chromium, firefox, webkit):

```shell
pytest --browser firefox
```

Run tests in multiple browsers:

```shell
pytest --browser chromium --browser webkit
```

If you are running into issues where it states a browser needs to be installed run:

```shell
playwright install
```

For further guidance on writing tests https://playwright.dev/python/docs/writing-tests

## Code formatting and linting

The Flake8 linter looks for code quality issues. Ensure there are no flake8 issues before committing. To run it:

```shell
flake8
```

All code should be formatted with black and isort before committing. To run them:

```shell
black .
isort .
```

## Features

Please refer to the specific packages documentation for more details.

### Asset management

Custom CSS and JavaScript files are merged and compressed using [Flask Assets](https://flask-assets.readthedocs.io/en/latest/) and [Webassets](https://webassets.readthedocs.io/en/latest/). This takes all `*.css` files in `app/static/src/css` and all `*.js` files in `app/static/src/js` and outputs a single compressed file to both `app/static/dist/css` and `app/static/dist/js` respectively.

CSS is [minified](https://en.wikipedia.org/wiki/Minification_(programming)) using [CSSMin](https://github.com/zacharyvoase/cssmin) and JavaScript is minified using [JSMin](https://github.com/tikitu/jsmin/). This removes all whitespace characters, comments and line breaks to reduce the size of the source code, making its transmission over a network more efficient.

Flask-Assets provides a built-in cache system to improve performance by caching compiled assets. However, this can
sometimes lead to issues where changes to your source files are not immediately reflected in the compiled output.

Flask-Assets uses `ASSETS_MANIFEST` which enables the cache manifest feature. Flask-Assets will generate a cache manifest 
file containing the paths to the compiled asset files. These are used to help with the hashing on generated asset files.

Note: When you start developing with Flask, you'll see a directory appear `app/static/webasset-cache`. webassets-cache
stores the asset manifest. If for some reason Flask-Assets is not picking up your changes to files, clear the folder of
its caches. 

### Cache busting

Merged and compressed assets are browser cache busted on update by modifying their URL with their MD5 hash using [Flask Assets](https://flask-assets.readthedocs.io/en/latest/) and [Webassets](https://webassets.readthedocs.io/en/latest/). The MD5 hash is appended to the file name, for example `custom-d41d8cd9.css` instead of a query string, to support certain older browsers and proxies that ignore the querystring in their caching behaviour.

### Forms generation and validation

Uses [Flask WTF](https://flask-wtf.readthedocs.io/en/stable/) and [WTForms](https://wtforms.readthedocs.io) to define and validate forms. Forms are rendered in your template using regular Jinja syntax.

### Form error handling

If a submitted form has any validation errors, an [error summary component](https://design-system.service.gov.uk/components/error-summary/) is shown at the top of the page, along with individual field [error messages](https://design-system.service.gov.uk/components/error-message/). This follows the GOV.UK Design System [validation pattern](https://design-system.service.gov.uk/patterns/validation/) and is built into the base page template.

### Flash messages

Messages created with Flask's `flash` function will be rendered using the GOV.UK Design System [notification banner component](https://design-system.service.gov.uk/components/notification-banner/). By default the blue "important" banner style will be used, unless a category of "success" is passed to use the green version.

### CSRF protection

Uses [Flask WTF](https://flask-wtf.readthedocs.io/en/stable/) to enable [Cross Site Request Forgery](https://en.wikipedia.org/wiki/Cross-site_request_forgery) protection per form and for the whole app.

CSRF errors are handled by creating a [flash message](#flash-messages) notification banner to inform the user that the form they submitted has expired.

### HTTP security headers

Uses [Flask Talisman](https://github.com/GoogleCloudPlatform/flask-talisman) to set HTTP headers that can help protect against a few common web application security issues.

- Forces all connections to `https`, unless running with debug enabled.
- Enables [HTTP Strict Transport Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security).
- Sets Flask's session cookie to `secure`, so it will never be set if your application is somehow accessed via a non-secure connection.
- Sets Flask's session cookie to `httponly`, preventing JavaScript from being able to access its content.
- Sets [X-Frame-Options](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options) to `SAMEORIGIN` to avoid [clickjacking](https://en.wikipedia.org/wiki/Clickjacking).
- Sets [X-XSS-Protection](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection) to enable a cross site scripting filter for IE and Safari (note Chrome has removed this and Firefox never supported it).
- Sets [X-Content-Type-Options](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options) to prevent content type sniffing.
- Sets a strict [Referrer-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy) of `strict-origin-when-cross-origin` that governs which referrer information should be included with requests made.

### Content Security Policy

A strict default [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP) (CSP) is set using [Flask Talisman](https://github.com/GoogleCloudPlatform/flask-talisman) to mitigate [Cross Site Scripting](https://developer.mozilla.org/en-US/docs/Web/Security/Types_of_attacks#cross-site_scripting_xss) (XSS) and packet sniffing attacks. This prevents loading any resources that are not in the same domain as the application.

### Response compression

Uses [Flask Compress](https://github.com/colour-science/flask-compress) to compress response data. This inspects the `Accept-Encoding` request header, compresses using either gzip, deflate or brotli algorithms and sets the `Content-Encoding` response header. HTML, CSS, XML, JSON and JavaScript MIME types will all be compressed.

### Rate limiting

Uses [Flask Limiter](https://flask-limiter.readthedocs.io/en/stable/) to set request rate limits on routes. The default rate limit is 2 requests per second _and_ 60 requests per minute (whichever is hit first) based on the client's remote IP address. Every time a request exceeds the rate limit, the view function will not get called and instead a [HTTP 429](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429) status will be returned.

Rate limit storage can be backed by [Redis](https://redis.io/) using the `RATELIMIT_STORAGE_URL` config value in `config.py`, or fall back to in-memory if not present. Rate limit information will also be added to various [response headers](https://flask-limiter.readthedocs.io/en/stable/#rate-limiting-headers).

Otherwise, please see the [contribution guidelines](CONTRIBUTING.md) for how to raise a bug report or feature request.
