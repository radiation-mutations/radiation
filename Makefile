AUTOFLAKE_OPTS ?= --remove-all-unused-imports --ignore-init-module-imports
PYTEST_OPTS ?= --cov radiation --cov radiation_cli --cov-report xml

default: format lint test

.PHONY: format lint install default

install:
	poetry install

lint:
	poetry run flake8
	poetry run mypy .

format:
	poetry run isort .
	poetry run black .
	poetry run autoflake $(AUTOFLAKE_OPTS) -i -r .

test:
	poetry run pytest $(PYTEST_OPTS)