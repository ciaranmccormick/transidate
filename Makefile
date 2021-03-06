SHELL:=/usr/bin/env bash

.PHONY: lint
lint:
	poetry run mypy transidate tests/*.py
	poetry run flake8 transidate tests/*.py

.PHONY: unit
unit:
	poetry run pytest --cov=transidate --cov-branch --cov-fail-under=90 tests/
	poetry run coverage html

.PHONY: package
package:
	poetry check
	poetry run pip check
	poetry run safety check --full-report

.PHONY: test
test: lint package unit
