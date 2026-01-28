# Check if you can get legal aid

[![Ministry of Justice Repository Compliance Badge](https://github-community.service.justice.gov.uk/repository-standards/api/laa-access-civil-legal-aid/badge)](https://github-community.service.justice.gov.uk/repository-standards/laa-access-civil-legal-aid)

## Getting started

## Local install for development
You can run this project in one of two ways:

- Local development setup (Python + Node on your machine)

- Docker (recommended for quick setup or parity with deployed environments)

👉 Pick one — you don’t need both.

## Local development setup:

Create a virtual environment and install the python dependencies:

> You need python 3.13 for this project

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/generated/requirements-development.txt
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

Now you can browse: <http://127.0.0.1:8020>

(The default port for flask apps is 5000, but on Macs this is often found to conflict with Apple's Airplay service, hence using another port here.)

## Running in Docker

For local development and deployments, run the below code to create Access and the CLA Backend:

```shell
./run_local.sh
```

You can also run Access as a standalone via:

```shell
./run_local_standalone.sh
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

For further guidance on writing tests <https://playwright.dev/python/docs/writing-tests>

## Code formatting and linting

The following will:

- Generate requirement.txt files from files inside requirements/source/_.in and put them into requirements/generated/_.txt
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

### Manually running secret detection

GitLeaks is executed at `pre-hook` commit and can be executed locally by running the following command.

```bash
 prek install # If not already done
 prek run
```

Same scans are also executed on the pipeline under `SCA` alongside with Trufflehog.

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

1. Run `./bin/translate.sh`
2. Update `app/translations/cy/LC_MESSAGES/messages.po` with welsh text
3. Run `pybabel compile -d app/translations -l cy -f`

## Git hooks

Repository uses [MoJ DevSecOps hooks](https://github.com/ministryofjustice/devsecops-hooks) to ensure `pre-commit` git hook is evaluated for series of checks before pushing the changes from staging area. Engineers should ensure `pre-commit` hook is configured and activated.

1. **Installation**:

   Ensure [prek](https://github.com/j178/prek?tab=readme-ov-file#installation) is installed globally

   Linux / MacOS

   ```bash
   curl --proto '=https' --tlsv1.2 -LsSf https://raw.githubusercontent.com/ministryofjustice/devsecops-hooks/e85ca6127808ef407bc1e8ff21efed0bbd32bb1a/prek/prek-installer.sh | sh
   ```

   or

   ```bash
   brew install prek
   ```

   Windows

   ```bash
   powershell -ExecutionPolicy ByPass -c "irm https://raw.githubusercontent.com/ministryofjustice/devsecops-hooks/e85ca6127808ef407bc1e8ff21efed0bbd32bb1a/prek/prek-installer.ps1 | iex"
   ```

2. **Activation**

   Execute the following command in the repository directory

   ```bash
   prek install
   ```

3. **Test**

    To dry-run the hook

   ```bash
   prek run
   ```

## 🔧 Configuration

### Exclusion list

One can exclude files and directories by adding them to `exclude` property. Exclude property accepts [regular expression](https://pre-commit.com/#regular-expressions).

Ignore everything under `reports` and `docs` directories for `baseline` hook as an example.

```yaml
   repos:
     - repo: https://github.com/ministryofjustice/devsecops-hooks
       rev: v1.0.0
       hooks:
         - id: baseline
            exclude: |
            ^reports/|
            ^docs/
```

Or one can also create a file with list of exclusions.

```yaml
repos:
  - repo: https://github.com/ministryofjustice/devsecops-hooks
    rev: v1.0.0
    hooks:
      - id: baseline
        exclude: .pre-commit-ignore
```
