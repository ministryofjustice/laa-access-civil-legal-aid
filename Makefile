.PHONY: update-deps

update-deps:  ## Update all requirements files
	pip-compile --no-annotate --upgrade --output-file=requirements/generated/requirements-development.txt requirements/source/requirements-development.in
	pip-compile --no-annotate --upgrade --output-file=requirements/generated/requirements-linting.txt requirements/source/requirements-linting.in
	pip-compile --no-annotate --upgrade --output-file=requirements/generated/requirements-production.txt requirements/source/requirements-production.in
