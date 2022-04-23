AUTOFLAKE_OPTS ?= --remove-all-unused-imports --ignore-init-module-imports

default: format lint

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