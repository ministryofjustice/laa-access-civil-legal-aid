# Access Civil Legal Aid

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

For this you'll need to install node. 

`npm install`

Once installed you now have access to GOVUK components, stylesheets and JS via the `node_module`

To copy some of the assets you'll need into your project, run the following:

`npm run build`

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
flask --app app run --debug --port=8000
```

Now you can browse: http://127.0.0.1:8000

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

The Ruff linter looks for code quality issues. Ensure there are no ruff issues before committing. 

To lint all files in the directory, run:

```shell
ruff check
```

To format all files in the directory, run:
```shell
ruff format
```