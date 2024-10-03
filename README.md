# Access Civil Legal Aid

[![Standards Icon]][Standards Link]

# Getting started

## Local install for development:

### Setup

Create a virtual environment and install the python dependencies:

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.in -r requirements_dev.in
```

### Assets setup

For this you'll need to install node > v20.9.0.

```bash
nvm install --lts
nvm use --lts
```

```bash
npm install
```

Once installed you now have access to GOVUK components, stylesheets and JS via the `node_module`

To copy some of the assets you'll need into your project, run the following:

```bash
npm run build
```

Ensure you do this before starting your Flask project as you're JS and SCSS imports will fail in the flask run.

### Configuration environment variables

Create your local config file `.env` from the template file:

```shell
cp .env.example .env
```

Don't worry, you can't commit your `.env` file.

### Run the service

```shell
source .venv/bin/activate
flask --app app run --debug --port=8020
```

Now you can browse: http://127.0.0.1:8020

(The default port for flask apps is 5000, but on Macs this is often found to conflict with Apple's Airplay service, hence using another port here.)

## Running in Docker

For local development and deployments, run the below code:

```shell
./run_local.sh
```

## Testing

To run the tests:

```shell
python -m pytest --cov=app --cov-report=term-missing --cov-branch
```

## Playwright Testing

To run all tests:

```shell
pytest
```

To run unit tests:

```shell
pytest tests/unit_tests
```

To run functional/non-functional tests:

```shell
pytest tests/functional_tests
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
The following will:
- Generate requirement.txt files from files inside requirements/source/*.in and put them into requirements/generated/*.txt
- Run linting checks with ruff

```shell
pre-commit install
```
### Manually running linting
The Ruff linter looks for code quality issues. Ensure there are no ruff issues before committing. 

To lint all files in the directory, run:

```shell
ruff check
```

To format all files in the directory, run:
```shell
ruff format
```
## Translation
We are using the [Flask-Babel](https://python-babel.github.io/flask-babel/#) package to translate text.
There are 4 key components to translating text on the website.
1. babel.cfg - Identifies which files to look for strings that can be translated
2. ./bin/translate.sh - Script to collect/update all translatable strings
3. pybabel compile - Should be run after updating any messages.po files. The full command is given in the output of translate.sh script
4. There are two languages(English and Welsh) available on the site. No translation is provided for English as that is the default language

### How to translate text in template
1. Wrap text in `{% trans %}...{% endtrans %}`
2. Run `./bin/translate.sh`
3. Update `app/translations/cy/LC_MESSAGES/messages.po` with welsh text
4. Run `pybabel compile -d app/translations -l cy -f`

### How to translate text in python
```
from flask_babel import lazy_gettext as _
_("text to translate")
```
2. Run `./bin/translate.sh`
3. Update `app/translations/cy/LC_MESSAGES/messages.po` with welsh text
4. Run `pybabel compile -d app/translations -l

[Standards Link]: https://operations-engineering-reports.cloud-platform.service.justice.gov.uk/public-report/laa-access-civil-legal-aid "Repo standards badge."
[Standards Icon]: https://img.shields.io/endpoint?labelColor=231f20&color=005ea5&style=for-the-badge&label=MoJ%20Compliant&url=https%3A%2F%2Foperations-engineering-reports.cloud-platform.service.justice.gov.uk%2Fapi%2Fv1%2Fcompliant_public_repositories%2Fendpoint%2Flaa-access-civil-legal-aid&logo=data:image/png;base64,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